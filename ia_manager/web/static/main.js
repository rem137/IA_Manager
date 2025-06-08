let currentProject = null;
let currentTask = null;

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
        li.onclick = () => openTask(t.id);
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
    closeTask();
}

async function openTask(id) {
    currentTask = id;
    const res = await fetch(`/api/tasks/${id}`);
    const data = await res.json();
    document.getElementById('detail-name').textContent = data.name;
    document.getElementById('detail-desc').textContent = data.description || 'No description';
    document.getElementById('detail-deadline').textContent = data.deadline || 'N/A';
    const modal = document.getElementById('task-modal');
    modal.style.display = 'flex';
}

function closeTask() {
    document.getElementById('task-modal').style.display = 'none';
    currentTask = null;
}

async function loadNotifications() {
    const res = await fetch('/api/notifications');
    const notes = await res.json();
    const container = document.getElementById('notifications');
    container.innerHTML = '';
    notes.forEach(n => {
        if (n.status !== 'pending') return;
        const div = document.createElement('div');
        div.className = 'notification';
        const msg = document.createElement('span');
        msg.textContent = n.message;
        const ok = document.createElement('button');
        ok.textContent = '✔';
        ok.onclick = () => respondNotif(n.id, 'accept');
        const no = document.createElement('button');
        no.textContent = '✖';
        no.onclick = () => respondNotif(n.id, 'decline');
        div.appendChild(msg);
        div.appendChild(ok);
        div.appendChild(no);
        container.appendChild(div);
    });
}

async function respondNotif(id, action) {
    await fetch(`/api/notifications/${id}/${action}`, { method: 'POST' });
    loadNotifications();
}

document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    loadNotifications();
    setInterval(loadNotifications, 5000);
});
