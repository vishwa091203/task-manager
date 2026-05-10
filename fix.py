dashboard = """{%extends "base.html"%}{%block content%}
<h2 style="margin-bottom:20px">Dashboard</h2>
<div class="stat-grid">
<div class="stat-card"><h2 id="total" style="color:#4f46e5">0</h2><p>Total Tasks</p></div>
<div class="stat-card"><h2 id="todo" style="color:#f59e0b">0</h2><p>To Do</p></div>
<div class="stat-card"><h2 id="progress" style="color:#3b82f6">0</h2><p>In Progress</p></div>
<div class="stat-card"><h2 id="done" style="color:#10b981">0</h2><p>Done</p></div>
</div>
<div class="card">
<h3 style="margin-bottom:15px">Overview</h3>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Overdue Tasks</td><td><span id="overdue" class="badge badge-overdue">0</span></td></tr>
<tr><td>Logged in as</td><td><span id="username">-</span></td></tr>
<tr><td>Your Role</td><td><span id="role" class="badge badge-progress">-</span></td></tr>
</table>
</div>
<script>
async function loadDashboard() {
const res = await fetch('/dashboard/', {headers: {'Authorization': 'Bearer ' + getToken()}});
if (!res.ok) { logout(); return; }
const data = await res.json();
document.getElementById('total').textContent = data.total_tasks;
document.getElementById('todo').textContent = data.todo;
document.getElementById('progress').textContent = data.in_progress;
document.getElementById('done').textContent = data.done;
document.getElementById('overdue').textContent = data.overdue;
document.getElementById('role').textContent = data.role;
document.getElementById('username').textContent = data.user;
}
loadDashboard();
</script>
{%endblock%}"""

project = """{%extends "base.html"%}{%block content%}
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
<h2>Projects</h2>
<button class="btn btn-primary" onclick="document.getElementById('create-form').style.display='block'">+ New Project</button>
</div>
<div class="card" id="create-form" style="display:none">
<h3 style="margin-bottom:15px">Create Project</h3>
<label>Project Name</label>
<input type="text" id="p-name" placeholder="Project name">
<label>Description</label>
<textarea id="p-desc" rows="3" placeholder="Description"></textarea>
<button class="btn btn-primary" onclick="createProject()">Create</button>
</div>
<div class="card">
<table>
<thead><tr><th>Name</th><th>Description</th><th>Actions</th></tr></thead>
<tbody id="projects-list"><tr><td colspan="3">Loading...</td></tr></tbody>
</table>
</div>
<script>
async function loadProjects() {
const res = await fetch('/projects/', {headers: {'Authorization': 'Bearer ' + getToken()}});
const data = await res.json();
const tbody = document.getElementById('projects-list');
if (!data.length) { tbody.innerHTML = '<tr><td colspan="3">No projects yet</td></tr>'; return; }
tbody.innerHTML = data.map(function(p) {
return '<tr><td><strong>' + p.name + '</strong></td><td>' + (p.description || '-') + '</td><td><a href="/tasks-page?project=' + p.id + '">View Tasks</a></td></tr>';
}).join('');
}
async function createProject() {
const name = document.getElementById('p-name').value;
const description = document.getElementById('p-desc').value;
const res = await fetch('/projects/', {
method: 'POST',
headers: {'Authorization': 'Bearer ' + getToken(), 'Content-Type': 'application/json'},
body: JSON.stringify({name, description})
});
if (res.ok) { document.getElementById('create-form').style.display='none'; loadProjects(); }
else { const d = await res.json(); alert(d.detail); }
}
loadProjects();
</script>
{%endblock%}"""

tasks = """{%extends "base.html"%}{%block content%}
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
<h2>Tasks</h2>
<button class="btn btn-primary" onclick="document.getElementById('create-form').style.display='block'">+ New Task</button>
</div>
<div class="card" id="create-form" style="display:none">
<h3 style="margin-bottom:15px">Create Task</h3>
<label>Title</label>
<input type="text" id="t-title" placeholder="Task title">
<label>Description</label>
<textarea id="t-desc" rows="2" placeholder="Description"></textarea>
<label>Project</label>
<select id="t-project"></select>
<label>Due Date</label>
<input type="datetime-local" id="t-due">
<button class="btn btn-primary" onclick="createTask()">Create Task</button>
</div>
<div class="card">
<table>
<thead><tr><th>Title</th><th>Project</th><th>Assignee</th><th>Status</th><th>Due</th><th>Change Status</th></tr></thead>
<tbody id="tasks-list"><tr><td colspan="6">Loading...</td></tr></tbody>
</table>
</div>
<script>
async function loadData() {
const token = getToken();
const headers = {'Authorization': 'Bearer ' + token};
const pr = await fetch('/projects/', {headers: headers}).then(function(r){ return r.json(); });
const tk = await fetch('/tasks/', {headers: headers}).then(function(r){ return r.json(); });
document.getElementById('t-project').innerHTML = pr.map(function(p){
return '<option value="' + p.id + '">' + p.name + '</option>';
}).join('');
const tbody = document.getElementById('tasks-list');
if (!tk.length) { tbody.innerHTML = '<tr><td colspan="6">No tasks yet</td></tr>'; return; }
tbody.innerHTML = tk.map(function(t) {
const badge = t.status === 'todo' ? 'badge-todo' : t.status === 'in_progress' ? 'badge-progress' : 'badge-done';
const label = t.status === 'in_progress' ? 'In Progress' : t.status === 'todo' ? 'To Do' : 'Done';
const due = t.due_date ? new Date(t.due_date).toLocaleDateString() : '-';
return '<tr><td><strong>' + t.title + '</strong><br><small style="color:#888">' + (t.description || '') + '</small></td><td>' + t.project_id + '</td><td>' + (t.assignee_id || 'Unassigned') + '</td><td><span class="badge ' + badge + '">' + label + '</span></td><td>' + due + '</td><td><select onchange="updateStatus(' + t.id + ', this.value)" style="width:auto;margin:0;padding:5px"><option value="todo"' + (t.status==='todo'?' selected':'') + '>To Do</option><option value="in_progress"' + (t.status==='in_progress'?' selected':'') + '>In Progress</option><option value="done"' + (t.status==='done'?' selected':'') + '>Done</option></select></td></tr>';
}).join('');
}
async function createTask() {
const body = {
title: document.getElementById('t-title').value,
description: document.getElementById('t-desc').value,
project_id: parseInt(document.getElementById('t-project').value),
due_date: document.getElementById('t-due').value || null
};
const res = await fetch('/tasks/', {
method: 'POST',
headers: {'Authorization': 'Bearer ' + getToken(), 'Content-Type': 'application/json'},
body: JSON.stringify(body)
});
if (res.ok) { document.getElementById('create-form').style.display='none'; loadData(); }
else { const d = await res.json(); alert(d.detail); }
}
async function updateStatus(taskId, status) {
await fetch('/tasks/' + taskId, {
method: 'PATCH',
headers: {'Authorization': 'Bearer ' + getToken(), 'Content-Type': 'application/json'},
body: JSON.stringify({status: status})
});
loadData();
}
loadData();
</script>
{%endblock%}"""

with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard)
with open('templates/project.html', 'w') as f:
    f.write(project)
with open('templates/tasks.html', 'w') as f:
    f.write(tasks)

print("All 3 template files written successfully!")