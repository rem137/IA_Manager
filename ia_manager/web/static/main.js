let currentProject = null;
let currentTask = null;

function showView(id) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
    document.querySelectorAll('#sidebar a').forEach(a => {
        a.classList.toggle('active', a.dataset.view === id);
    });
    if (id === 'tasks-view') loadAllTasks();
    if (id === 'dashboard-view') loadDashboard();
    if (id === 'calendar-view') loadCalendar();
}

async function loadAllTasks() {
    const res = await fetch('/api/projects');
    const projs = await res.json();
    const list = document.getElementById('all-task-list');
    list.innerHTML = '';
    projs.forEach(p => {
        p.tasks.forEach(t => {
            const li = document.createElement('li');
            li.className = 'task-item';
            if (t.status === 'done') li.classList.add('done');
            li.textContent = `${p.name}: ${t.name}`;
            list.appendChild(li);
        });
    });
}

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

function openTaskForm() {
    if (!currentProject) return;
    document.getElementById('task-form').style.display = 'flex';
}

function closeTaskForm() {
    document.getElementById('task-form').style.display = 'none';
}

async function submitTask() {
    if (!currentProject) return;
    const name = document.getElementById('task-name-input').value.trim();
    const desc = document.getElementById('task-desc-input').value.trim();
    const deadline = document.getElementById('task-deadline-input').value || null;
    const start = document.getElementById('task-start-input').value || null;
    const end = document.getElementById('task-end-input').value || null;
    const hours = parseFloat(document.getElementById('task-hours-input').value) || null;
    if (!name) return;
    await fetch(`/api/projects/${currentProject}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: desc, deadline, planned_start: start, planned_end: end, planned_hours: hours })
    });
    document.getElementById('task-name-input').value = '';
    document.getElementById('task-desc-input').value = '';
    document.getElementById('task-deadline-input').value = '';
    document.getElementById('task-start-input').value = '';
    document.getElementById('task-end-input').value = '';
    document.getElementById('task-hours-input').value = '';
    closeTaskForm();
    selectProject(currentProject, document.getElementById('tasks-title').dataset.project);
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
    const plan = document.getElementById('detail-plan');
    if (plan) {
        const start = data.planned_start ? `Start: ${data.planned_start}` : '';
        const end = data.planned_end ? ` End: ${data.planned_end}` : '';
        const hours = data.planned_hours ? ` (${data.planned_hours}h)` : '';
        plan.textContent = start || end || hours ? `${start}${end}${hours}` : 'No plan';
    }
    document.getElementById('detail-time').textContent = formatTime(data.time_spent);
    const btn = document.getElementById('start-stop-btn');
    btn.textContent = data.started ? 'Stop' : 'Start';
    const modal = document.getElementById('task-modal');
    modal.style.display = 'flex';
}

function closeTask() {
    document.getElementById('task-modal').style.display = 'none';
    currentTask = null;
}

function formatTime(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return `${h}h ${m}m`;
}

async function toggleTimer() {
    if (!currentTask) return;
    const btn = document.getElementById('start-stop-btn');
    if (btn.textContent === 'Start') {
        await fetch(`/api/tasks/${currentTask}/start`, { method: 'POST' });
        btn.textContent = 'Stop';
    } else {
        const res = await fetch(`/api/tasks/${currentTask}/stop`, { method: 'POST' });
        const data = await res.json();
        document.getElementById('detail-time').textContent = formatTime(data.time_spent);
        btn.textContent = 'Start';
    }
    if (currentProject) selectProject(currentProject, document.getElementById('tasks-title').dataset.project);
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
    document.querySelectorAll('#sidebar a').forEach(a => {
        a.onclick = (e) => { e.preventDefault(); showView(a.dataset.view); };
    });
    loadDeadlines();
    document.getElementById('new-task-btn').onclick = openTaskForm;
    document.getElementById('send-btn').onclick = sendMessage;
    document.getElementById('message').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
    });
    setInterval(loadNotifications, 5000);
    setInterval(loadDeadlines, 60000);
    feather.replace();
    document.getElementById('accept-proposal').onclick = () => alert('Tâche acceptée');
    document.getElementById('decline-proposal').onclick = loadDashboard;
    showView('dashboard-view');
});


async function loadDeadlines() {
    const res = await fetch('/api/deadlines');
    const tasks = await res.json();
    const list = document.getElementById('deadline-list');
    list.innerHTML = '';
    tasks.forEach(t => {
        const li = document.createElement('li');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.onchange = () => markDone(t.id);
        const span = document.createElement('span');
        span.textContent = `${t.task} - ${t.project}`;
        li.appendChild(checkbox);
        li.appendChild(span);
        list.appendChild(li);
    });
}

async function fetchRecommendation() {
    const res = await fetch('/api/recommendations');
    const recs = await res.json();
    return recs.length ? recs[0] : 'No suggestions';
}

async function loadDashboard() {
    const rec = await fetchRecommendation();
    document.getElementById('proposal-text').textContent = rec;
}


async function sendMessage() {
    const input = document.getElementById('message');
    const msg = input.value.trim();
    if (!msg) return;
    const log = document.getElementById('chat-log');
    const u = document.createElement('div');
    u.className = 'user-msg';
    u.textContent = msg;
    log.appendChild(u);
    log.scrollTop = log.scrollHeight;
    input.value = '';

    const r = document.createElement('div');
    r.className = 'bot-msg thinking';
    log.appendChild(r);
    log.scrollTop = log.scrollHeight;

    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
    });
    r.classList.remove('thinking');
    if (res.ok) {
        const data = await res.json();
        r.textContent = data.reply || '';
        if (data.logs && data.logs.length) {
            const pre = document.createElement('pre');
            pre.className = 'action-log';
            pre.textContent = data.logs.join('\n');
            log.appendChild(pre);
        }
    } else {
        r.textContent = 'Error';
    }
    log.scrollTop = log.scrollHeight;
}

async function loadCalendar() {
    const table = document.getElementById('calendar-table');
    if (!table) return;
    const now = new Date();
    const monday = new Date(now);
    monday.setDate(now.getDate() - now.getDay() + 1);
    const startStr = monday.toISOString().slice(0, 10);
    const res = await fetch(`/api/calendar/week?start=${startStr}`);
    const data = await res.json();
    table.innerHTML = '';
    const headerRow = document.createElement('tr');
    const days = [];
    for (let i = 0; i < 7; i++) {
        const d = new Date(monday);
        d.setDate(monday.getDate() + i);
        const th = document.createElement('th');
        th.textContent = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
        headerRow.appendChild(th);
        days.push(d.toISOString().slice(0, 10));
    }
    table.appendChild(headerRow);
    const row = document.createElement('tr');
    days.forEach(ds => {
        const td = document.createElement('td');
        const items = data[ds] || [];
        items.sort((a,b) => (a.time || '').localeCompare(b.time || ''));
        items.forEach(it => {
            const div = document.createElement('div');
            div.className = 'cal-item';
            div.textContent = (it.time ? it.time + ' - ' : '') + `${it.task} (${it.project})`;
            td.appendChild(div);
        });
        row.appendChild(td);
    });
    table.appendChild(row);
}
