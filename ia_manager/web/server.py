from flask import Flask, jsonify, request, render_template, Response
from datetime import datetime, timedelta
import re
import json
from ..services import storage, planner, logger, memory
from .. import assistant
from ..models.project import Project
from ..models.task import Task
from ..models.notification import Notification

app = Flask(__name__, template_folder='templates', static_folder='static')

# simple in-memory notification queue
notifications: list[Notification] = []


def _extract_actions(logs: list[str]) -> list[str]:
    actions: list[str] = []
    for line in logs:
        m = re.search(r"Appel de la fonction: (\w+)", line)
        if m:
            name = m.group(1).replace('_', ' ')
            actions.append(f"En train de {name}...")
    return actions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = storage.load_projects()
    return jsonify([p.to_dict() for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    projects = storage.load_projects()
    project_id = max([p.id for p in projects], default=0) + 1
    project = Project(
        id=project_id,
        name=data.get('name', f'Project {project_id}'),
        description=data.get('description', ''),
        priority=data.get('priority', 3),
        deadline=data.get('deadline'),
    )
    projects.append(project)
    storage.save_projects(projects)
    logger.log(f"Web: added project {project.name}")
    return jsonify(project.to_dict())

@app.route('/api/projects/<int:pid>', methods=['GET'])
def get_project(pid):
    projects = storage.load_projects()
    proj = next((p for p in projects if p.id == pid), None)
    if not proj:
        return jsonify({'error': 'not found'}), 404
    return jsonify(proj.to_dict())

@app.route('/api/projects/<int:pid>', methods=['PUT', 'DELETE'])
def modify_project(pid):
    """Rename or delete a project."""
    projects = storage.load_projects()
    proj = next((p for p in projects if p.id == pid), None)
    if not proj:
        return jsonify({'error': 'not found'}), 404

    if request.method == 'DELETE':
        projects.remove(proj)
        storage.save_projects(projects)
        logger.log(f"Web: deleted project {pid}")
        return jsonify({'status': 'ok'})

    data = request.json
    proj.name = data.get('name', proj.name)
    proj.description = data.get('description', proj.description)
    proj.priority = data.get('priority', proj.priority)
    proj.deadline = data.get('deadline', proj.deadline)
    storage.save_projects(projects)
    logger.log(f"Web: updated project {pid}")
    return jsonify(proj.to_dict())

@app.route('/api/projects/<int:pid>/tasks', methods=['POST'])
def add_task(pid):
    data = request.json
    projects = storage.load_projects()
    proj = next((p for p in projects if p.id == pid), None)
    if not proj:
        return jsonify({'error': 'not found'}), 404
    task_id = max([t.id for t in proj.tasks], default=0) + 1
    task = Task(
        id=task_id,
        name=data.get('name', f'Task {task_id}'),
        estimated=data.get('estimated'),
        deadline=data.get('deadline'),
        importance=data.get('importance', 3),
        description=data.get('description', ''),
        planned_start=data.get('planned_start'),
        planned_end=data.get('planned_end'),
        planned_hours=data.get('planned_hours'),
    )
    proj.tasks.append(task)
    storage.save_projects(projects)
    logger.log(f"Web: added task {task.name} to project {proj.name}")
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:tid>', methods=['GET'])
def get_task(tid):
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
                return jsonify(t.to_dict())
    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:tid>', methods=['PUT'])
def update_task(tid):
    data = request.json
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
                t.name = data.get('name', t.name)
                t.status = data.get('status', t.status)
                t.estimated = data.get('estimated', t.estimated)
                t.deadline = data.get('deadline', t.deadline)
                t.importance = data.get('importance', t.importance)
                t.description = data.get('description', t.description)
                t.planned_start = data.get('planned_start', t.planned_start)
                t.planned_end = data.get('planned_end', t.planned_end)
                t.planned_hours = data.get('planned_hours', t.planned_hours)
                storage.save_projects(projects)
                logger.log(f"Web: updated task {tid}")
                return jsonify(t.to_dict())
    return jsonify({'error': 'not found'}), 404


@app.route('/api/tasks/<int:tid>/start', methods=['POST'])
def start_task(tid):
    projects = storage.load_projects()
    now = datetime.utcnow().isoformat()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
                if not t.started:
                    t.started = now
                    storage.save_projects(projects)
                    logger.log(f"Web: started task {tid}")
                return jsonify({'status': 'started'})
    return jsonify({'error': 'not found'}), 404


@app.route('/api/tasks/<int:tid>/stop', methods=['POST'])
def stop_task(tid):
    projects = storage.load_projects()
    now = datetime.utcnow()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
                if t.started:
                    try:
                        st = datetime.fromisoformat(t.started)
                        t.time_spent += int((now - st).total_seconds())
                    except ValueError:
                        pass
                    t.started = None
                    storage.save_projects(projects)
                    logger.log(f"Web: stopped task {tid}")
                return jsonify({'time_spent': t.time_spent})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:tid>/done', methods=['POST'])
def mark_task_done(tid):
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
                if t.started:
                    try:
                        st = datetime.fromisoformat(t.started)
                        t.time_spent += int((datetime.utcnow() - st).total_seconds())
                    except ValueError:
                        pass
                    t.started = None
                t.status = 'done'
                storage.save_projects(projects)
                logger.log(f"Web: done task {tid}")
                return jsonify({'status': 'ok'})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:tid>', methods=['DELETE'])
def delete_task(tid):
    projects = storage.load_projects()
    for p in projects:
        for t in list(p.tasks):
            if t.id == tid:
                p.tasks.remove(t)
                storage.save_projects(projects)
                logger.log(f"Web: deleted task {tid}")
                return jsonify({'status': 'ok'})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/recommendations')
def recommendations():
    projs = storage.load_projects()
    recs = planner.suggest_tasks(projs)
    return jsonify(recs)


@app.route('/api/calendar/<date_str>')
def calendar_day(date_str: str):
    """Return tasks due on a given date (YYYY-MM-DD)."""
    try:
        day = datetime.fromisoformat(date_str).date()
    except ValueError:
        return jsonify({'error': 'bad date'}), 400

    projs = storage.load_projects()
    tasks = []
    for p in projs:
        for t in p.tasks:
            date_str = t.planned_start or t.deadline
            if not date_str:
                continue
            try:
                d = datetime.fromisoformat(date_str)
            except ValueError:
                continue
            if d.date() == day:
                tasks.append({
                    'project': p.name,
                    'task': t.name,
                    'time': d.strftime('%H:%M') if d.time().hour or d.time().minute else None
                })
    return jsonify(tasks)


@app.route('/api/calendar/week')
def calendar_week():
    """Return tasks scheduled in a 7-day window starting from the given date.
    Query param `start` expects YYYY-MM-DD and defaults to current week Monday.
    """
    start_str = request.args.get('start')
    if start_str:
        try:
            start = datetime.fromisoformat(start_str).date()
        except ValueError:
            return jsonify({'error': 'bad date'}), 400
    else:
        today = datetime.utcnow().date()
        start = today - timedelta(days=today.weekday())

    days = { (start + timedelta(days=i)).isoformat(): [] for i in range(7) }
    projs = storage.load_projects()
    for p in projs:
        for t in p.tasks:
            date_str = t.planned_start or t.deadline
            if not date_str:
                continue
            try:
                d = datetime.fromisoformat(date_str)
            except ValueError:
                continue
            date_key = d.date().isoformat()
            if date_key in days:
                days[date_key].append({
                    'project': p.name,
                    'task': t.name,
                    'time': d.strftime('%H:%M') if d.time().hour or d.time().minute else None
                })
    return jsonify(days)


@app.route('/api/deadlines')
def upcoming_deadlines():
    """Return tasks due in the next 7 days."""
    now = datetime.utcnow()
    projs = storage.load_projects()
    upcoming = []
    for p in projs:
        for t in p.tasks:
            date_str = t.planned_start or t.deadline
            if t.status == 'done' or not date_str:
                continue
            try:
                d = datetime.fromisoformat(date_str)
            except ValueError:
                continue
            if 0 <= (d - now).days <= 7:
                upcoming.append({'id': t.id, 'project': p.name, 'task': t.name, 'deadline': d.isoformat()})
    upcoming.sort(key=lambda x: x['deadline'])
    return jsonify(upcoming)


@app.route('/api/notifications', methods=['GET', 'POST'])
def notifications_api():
    if request.method == 'POST':
        data = request.json
        nid = max([n.id for n in notifications], default=0) + 1
        notif = Notification(id=nid, message=data.get('message', ''), action=data.get('action'))
        notifications.append(notif)
        logger.log(f"Web: added notification {nid}")
        return jsonify(notif.__dict__), 201
    return jsonify([n.__dict__ for n in notifications])


@app.route('/api/notifications/<int:nid>/<action>', methods=['POST'])
def handle_notification(nid, action):
    for n in notifications:
        if n.id == nid:
            n.status = action
            logger.log(f"Web: notification {nid} {action}")
            return jsonify({'status': 'ok'})
    return jsonify({'error': 'not found'}), 404


@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'no message'}), 400
    try:
        reply, logs = assistant.send_message_verbose(message)
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 500
    actions = _extract_actions(logs)
    return jsonify({'reply': reply, 'actions': actions})


@app.route('/api/chat/stream')
def chat_stream():
    message = request.args.get('message', '').strip()
    if not message:
        return 'no message', 400

    def generate():
        for event in assistant.send_message_events(message):
            yield 'data: ' + json.dumps(event) + '\n\n'

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/search')
def search_api():
    """Return a short context paragraph for the given query."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'result': ''})
    result = memory.get_context(query, max_chars=500)
    return jsonify({'result': result})


@app.route('/api/personality', methods=['GET', 'POST'])
def personality_api():
    """Get or update user personality."""
    if request.method == 'GET':
        user = memory.load_user()
        return jsonify(user.to_dict())
    data = request.json or {}
    user = memory.load_user()
    if 'name' in data:
        user.name = data['name']
    if 'sarcasm' in data:
        try:
            user.sarcasm = float(data['sarcasm'])
        except (TypeError, ValueError):
            pass
        user.sarcasm = max(0.0, min(1.0, user.sarcasm))
    memory.save_user(user)
    return jsonify(user.to_dict())


@app.route('/api/session_note', methods=['GET', 'POST'])
def session_note_api():
    """Get or update the custom session note."""
    if request.method == 'GET':
        return jsonify({'note': memory.load_custom_session_note()})
    data = request.json or {}
    memory.save_custom_session_note(data.get('note', ''))
    return jsonify({'note': data.get('note', '')})

if __name__ == '__main__':
    app.run(debug=True)
