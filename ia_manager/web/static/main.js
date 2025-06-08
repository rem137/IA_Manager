let currentProject = null;

async function loadProjects() {
    const res = await fetch('/api/projects');
    const projects = await res.json();
    const list = document.getElementById('project-list');
    list.innerHTML = '';
    projects.forEach(p => {
        const li = document.createElement('li');
        li.textContent = p.name;
        li.dataset.id = p.id;
        li.onclick = () => selectProject(p.id, p.name);
        if (p.id === currentProject) li.classList.add('selected');
        list.appendChild(li);
    });
}

async function selectProject(id, name) {
    currentProject = id;
    document.querySelectorAll('#project-list li').forEach(li => {
        li.classList.toggle('selected', parseInt(li.dataset.id) === id);
    });
    document.getElementById('tasks-title').textContent = `Tasks - ${name}`;
    const res = await fetch(`/api/projects/${id}`);
    const proj = await res.json();
    const list = document.getElementById('task-list');
    list.innerHTML = '';
    proj.tasks.forEach(t => {
        const li = document.createElement('li');
        li.textContent = t.name;
        if (t.status === 'done') li.classList.add('done');
        li.onclick = () => markDone(t.id);
        list.appendChild(li);
    });
}

async function createProject() {
    const name = document.getElementById('new-project-name').value.trim();
    if (!name) return;
    await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    document.getElementById('new-project-name').value = '';
    loadProjects();
}

async function createTask() {
    if (!currentProject) return;
    const name = document.getElementById('new-task-name').value.trim();
    if (!name) return;
    await fetch(`/api/projects/${currentProject}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    document.getElementById('new-task-name').value = '';
    selectProject(currentProject, document.getElementById('tasks-title').textContent);
}

async function markDone(id) {
    await fetch(`/api/tasks/${id}/done`, { method: 'POST' });
    if (currentProject) selectProject(currentProject, document.getElementById('tasks-title').textContent);
}

document.addEventListener('DOMContentLoaded', loadProjects);
