from flask import Flask, jsonify, request, render_template
from ..services import storage, planner, logger
from ..models.project import Project
from ..models.task import Task

app = Flask(__name__, template_folder='templates', static_folder='static')

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

@app.route('/api/tasks/<int:tid>/done', methods=['POST'])
def mark_task_done(tid):
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == tid:
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

if __name__ == '__main__':
    app.run(debug=True)
