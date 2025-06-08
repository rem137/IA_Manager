let currentProject = null;
let currentTask = null;

async function loadProjects() {
    const res = await fetch('/api/projects');
    const projects = await res.json();
    const list = document.getElementById('project-list');
    list.innerHTML = '';
    projects.forEach(p => {
        const li = document.createElement('li');
        li.className = 'project-item';
        if (p.id === currentProject) li.classList.add('selected');

        const name = document.createElement('span');
        name.className = 'proj-name';
        name.textContent = p.name;
        name.onclick = () => selectProject(p.id, p.name);

        const rename = document.createElement('button');
        rename.textContent = '✎';
        rename.className = 'icon';
        rename.onclick = () => renameProject(p.id, p.name);

        const del = document.createElement('button');
        del.textContent = '🗑';
        del.className = 'icon critical';
        del.onclick = () => deleteProject(p.id);

        li.appendChild(name);
        li.appendChild(rename);
        li.appendChild(del);
        li.dataset.id = p.id;
        list.appendChild(li);
    });
}

async function selectProject(id, name) {
    currentProject = id;
    document.querySelectorAll('#project-list li').forEach(li => {
        li.classList.toggle('selected', parseInt(li.dataset.id) === id);
    });
    const title = document.getElementById('tasks-title');
    title.textContent = name ? `Tasks for "${name}"` : 'Tasks';
    title.dataset.project = name;
    const res = await fetch(`/api/projects/${id}`);
    const proj = await res.json();
    const list = document.getElementById('task-list');
    list.innerHTML = '';
    proj.tasks.forEach(t => {
        const li = document.createElement('li');
        li.className = 'task-item';
        if (t.status === 'done') li.classList.add('done');

        const span = document.createElement('span');
        span.textContent = t.name;
        span.onclick = () => openTask(t.id);

        const doneBtn = document.createElement('button');
        doneBtn.textContent = '✓';
        doneBtn.className = 'icon';
        doneBtn.onclick = () => markDone(t.id);

        const delBtn = document.createElement('button');
        delBtn.textContent = '🗑';
        delBtn.className = 'icon critical';
        delBtn.onclick = () => deleteTask(t.id);

        li.appendChild(span);
        li.appendChild(doneBtn);
        li.appendChild(delBtn);
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

async function renameProject(id, current) {
    const name = prompt('Rename project', current);
    if (!name) return;
    await fetch(`/api/projects/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    loadProjects();
}

async function deleteProject(id) {
    if (!confirm('Delete this project?')) return;
    await fetch(`/api/projects/${id}`, { method: 'DELETE' });
    if (id === currentProject) {
        currentProject = null;
        document.getElementById('task-list').innerHTML = '';
        document.getElementById('tasks-title').textContent = 'Tasks';
    }
    loadProjects();
}

async function createTask() {
    if (!currentProject) return;
    const name = document.getElementById('new-task-name').value.trim();
    const deadline = document.getElementById('new-task-deadline').value || null;
    if (!name) return;
    await fetch(`/api/projects/${currentProject}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, deadline })
    });
    document.getElementById('new-task-name').value = '';
    document.getElementById('new-task-deadline').value = '';
    selectProject(currentProject, document.getElementById('tasks-title').textContent);
}

async function markDone(id) {
    await fetch(`/api/tasks/${id}/done`, { method: 'POST' });
    if (currentProject) selectProject(currentProject, document.getElementById('tasks-title').dataset.project);
    closeTask();
}

async function deleteTask(id) {
    if (!confirm('Delete this task?')) return;
    await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (currentProject) selectProject(currentProject, document.getElementById('tasks-title').dataset.project);
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
    const today = new Date().toISOString().slice(0,10);
    document.getElementById('plan-date').value = today;
    loadPlan(today);
    document.getElementById('plan-date').onchange = (e) => loadPlan(e.target.value);
    document.getElementById('recommend-btn').onclick = recommendTask;
    document.getElementById('theme-toggle').onclick = toggleTheme;
    document.getElementById('send-btn').onclick = sendMessage;
    document.getElementById('message').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
    });
    setInterval(loadNotifications, 5000);
});

async function loadPlan(date) {
    const res = await fetch(`/api/calendar/${date}`);
    const tasks = await res.json();
    const list = document.getElementById('plan-list');
    document.getElementById('plan-title').textContent = `Schedule for ${date}`;
    list.innerHTML = '';
    tasks.forEach(t => {
        const li = document.createElement('li');
        li.textContent = t.time ? `${t.time} - ${t.project}: ${t.task}`
                               : `${t.project}: ${t.task}`;
        list.appendChild(li);
    });
}

async function recommendTask() {
    const res = await fetch('/api/recommendations');
    const recs = await res.json();
    const div = document.getElementById('recommendation');
    div.textContent = recs.length ? recs[0] : 'No suggestions';
}

function toggleTheme() {
    document.body.classList.toggle('light');
}

function sendMessage() {
    const input = document.getElementById('message');
    const msg = input.value.trim();
    if (!msg) return;
    const log = document.getElementById('chat-log');
    const div = document.createElement('div');
    div.textContent = msg;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    input.value = '';
}
