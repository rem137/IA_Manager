from flask import Flask, jsonify, request, render_template
from datetime import datetime
from ..services import storage, planner, logger
from ..models.project import Project
from ..models.task import Task
from ..models.notification import Notification

app = Flask(__name__, template_folder='templates', static_folder='static')

# simple in-memory notification queue
notifications: list[Notification] = []

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
        description=data.get('description', '')
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
            if not t.deadline:
                continue
            try:
                d = datetime.fromisoformat(t.deadline)
            except ValueError:
                continue
            if d.date() == day:
                tasks.append({
                    'project': p.name,
                    'task': t.name,
                    'time': d.strftime('%H:%M') if d.time().hour or d.time().minute else None
                })
    return jsonify(tasks)


@app.route('/api/deadlines')
def upcoming_deadlines():
    """Return tasks due in the next 7 days."""
    now = datetime.utcnow()
    projs = storage.load_projects()
    upcoming = []
    for p in projs:
        for t in p.tasks:
            if t.status == 'done' or not t.deadline:
                continue
            try:
                d = datetime.fromisoformat(t.deadline)
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

if __name__ == '__main__':
    app.run(debug=True)
