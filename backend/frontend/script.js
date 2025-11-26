const tasks = [];

function renderTasks() {
  const list = document.getElementById('task-list');
  list.innerHTML = '';
  tasks.forEach((t, i) => {
    const li = document.createElement('li');
    li.className = 'task-item';
    li.innerHTML = `<strong>${t.title}</strong> <span class="small">| Due: ${t.due_date || '—'} | Effort: ${t.estimated_hours}h | Imp: ${t.importance}</span>
      <div><button onclick="removeTask(${i})">Remove</button></div>`;
    list.appendChild(li);
  });
}

function removeTask(i){
  tasks.splice(i,1);
  renderTasks();
}

document.getElementById('task-form').addEventListener('submit', (e)=>{
  e.preventDefault();
  const title = document.getElementById('title').value.trim();
  const due_date = document.getElementById('due_date').value || null;
  const estimated_hours = parseFloat(document.getElementById('estimated_hours').value) || 1;
  const importance = parseInt(document.getElementById('importance').value) || 5;
  const deps_raw = document.getElementById('dependencies').value.trim();
  const dependencies = deps_raw ? deps_raw.split(',').map(s=>s.trim()).filter(Boolean) : [];
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2,6);
  tasks.push({id, title, due_date, estimated_hours, importance, dependencies});
  renderTasks();
  document.getElementById('task-form').reset();
});

document.getElementById('add-bulk').addEventListener('click', ()=>{
  const raw = document.getElementById('bulk').value;
  if(!raw) return alert('Paste a JSON array first');
  try {
    const arr = JSON.parse(raw);
    if(!Array.isArray(arr)) throw new Error('Not array');
    arr.forEach(t=>{
      const id = t.id || (Date.now().toString(36) + Math.random().toString(36).slice(2,6));
      tasks.push({
        id,
        title: t.title || 'Untitled',
        due_date: t.due_date || null,
        estimated_hours: t.estimated_hours || 1,
        importance: t.importance || 5,
        dependencies: t.dependencies || []
      });
    });
    renderTasks();
    document.getElementById('bulk').value = '';
  } catch (err) {
    alert('Invalid JSON: ' + err.message);
  }
});

document.getElementById('analyze').addEventListener('click', async ()=>{
  if(tasks.length === 0) return alert('Add tasks first');
  const strategy = document.getElementById('strategy').value;

  const payload = tasks.map(t=>{

    return {
      id: t.id,
      title: t.title,
      due_date: t.due_date || null,
      estimated_hours: t.estimated_hours,
      importance: t.importance,
      dependencies: t.dependencies
    }
  });

  const resp = await fetch('/api/tasks/analyze/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await resp.json();
  if(!resp.ok){
    alert('Error: ' + JSON.stringify(data));
    return;
  }
  renderResults(data.results);
});

document.getElementById('suggest').addEventListener('click', async ()=>{
  if(tasks.length === 0) return alert('Add tasks first');
  const payload = tasks.map(t=>({
    id: t.id, title: t.title, due_date: t.due_date || null, estimated_hours: t.estimated_hours, importance: t.importance, dependencies: t.dependencies
  }));
  const qs = encodeURIComponent(JSON.stringify(payload));
  const url = `/api/tasks/suggest/?tasks=${qs}`;
  const resp = await fetch(url);
  const data = await resp.json();
  if(!resp.ok){
    alert('Error: ' + JSON.stringify(data));
    return;
  }
  renderSuggestions(data.top3, data.cycles || []);
});

function renderResults(results){
  const out = document.getElementById('results');
  out.innerHTML = '';
  results.forEach(r=>{
    const div = document.createElement('div');
    div.className = 'result-card ' + (r.score >= 0.6 ? 'score-high' : (r.score >= 0.35 ? 'score-med' : 'score-low'));
    div.innerHTML = `<strong>${r.title}</strong> <span class="badge">Score: ${r.score}</span>
      <div class="small">${r.explanation}</div>
      <div class="small">Details: due=${r.metadata.due_date} | est=${r.metadata.estimated_hours} | imp=${r.metadata.importance}</div>`;
    out.appendChild(div);
  });
}

function renderSuggestions(top3, cycles){
  const out = document.getElementById('results');
  out.innerHTML = '<h3>Top 3 Suggestions</h3>';
  top3.forEach(r=>{
    const div = document.createElement('div');
    div.className = 'result-card';
    div.innerHTML = `<strong>${r.title}</strong> <span class="badge">Score: ${r.score}</span>
      <div class="small">${r.explanation}</div>`;
    out.appendChild(div);
  });
  if(cycles && cycles.length){
    const cdiv = document.createElement('div');
    cdiv.className = 'result-card';
    cdiv.innerHTML = `<strong>Detected dependency cycles</strong><div class="small">${JSON.stringify(cycles)}</div>`;
    out.appendChild(cdiv);
  }
}

function renderEisenhowerMatrix(tasks) {
   
    document.querySelectorAll("#matrix ul").forEach(ul => ul.innerHTML = "");

    tasks.forEach(task => {
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        const today = new Date();

        let urgent = false;
        let important = false;

        
        if (dueDate && (dueDate - today) / (1000 * 60 * 60 * 24) <= 2) {
            urgent = true;
        }

       
        if (task.importance >= 7) {
            important = true;
        }

        const li = document.createElement("li");
        li.textContent = `${task.title} (Imp: ${task.importance})`;

        if (urgent && important) {
            document.querySelector("#urgent-important ul").appendChild(li);
        } else if (!urgent && important) {
            document.querySelector("#noturgent-important ul").appendChild(li);
        } else if (urgent && !important) {
            document.querySelector("#urgent-notimportant ul").appendChild(li);
        } else {
            document.querySelector("#noturgent-notimportant ul").appendChild(li);
        }
    });
}
