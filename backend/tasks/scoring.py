import datetime
from typing import Dict, List, Tuple, Any, Optional, Set

DEFAULT_WEIGHTS = {
    'urgency': 0.35,
    'importance': 0.30,
    'effort': 0.20,       
    'dependency': 0.15,
}

def days_until_due(due_date: Optional[datetime.date], today: Optional[datetime.date] = None) -> Optional[int]:
    if today is None:
        today = datetime.date.today()
    if due_date is None:
        return None
    return (due_date - today).days

def normalize(value: float, minv: float, maxv: float) -> float:
    if maxv == minv:
        return 0.0
    return max(0.0, min(1.0, (value - minv) / (maxv - minv)))

def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> List[List[int]]:
    id_map = {}
    for idx, t in enumerate(tasks):
        node_id = t.get('id', idx)
        id_map[node_id] = t

    adj = {}
    for idx, t in enumerate(tasks):
        node_id = t.get('id', idx)
        adj[node_id] = list(t.get('dependencies', []))

    visited = {}
    stack = []
    cycles = []

    def dfs(u):
        visited[u] = 1  # visiting
        stack.append(u)
        for v in adj.get(u, []):
            if v not in adj:
                continue
            if visited.get(v, 0) == 0:
                dfs(v)
            elif visited.get(v) == 1:
                # found cycle
                try:
                    i = stack.index(v)
                    cycles.append(stack[i:].copy())
                except ValueError:
                    cycles.append([v, u])
        stack.pop()
        visited[u] = 2

    for node in adj:
        if visited.get(node, 0) == 0:
            dfs(node)
    return cycles

def compute_dependency_scores(tasks: List[Dict[str, Any]]) -> Dict[Any, float]:
    id_map = {}
    for idx, t in enumerate(tasks):
        node_id = t.get('id', idx)
        id_map[node_id] = t

    dependents_count = {nid: 0 for nid in id_map}
    for nid, t in id_map.items():
        for dep in t.get('dependencies', []):
            if dep in dependents_count:
                dependents_count[dep] += 1

    if dependents_count:
        counts = list(dependents_count.values())
        maxc = max(counts)
        minc = min(counts)
        dep_scores = {}
        for nid, cnt in dependents_count.items():
            dep_scores[nid] = normalize(cnt, minc, maxc) if maxc != minc else (1.0 if cnt > 0 else 0.0)
    else:
        dep_scores = {}
    return dep_scores

def score_tasks(tasks: List[Dict[str, Any]], weights: Dict[str, float] = None, today: Optional[datetime.date] = None) -> List[Dict[str, Any]]:

    import datetime as _dt
    if weights is None:
        weights = DEFAULT_WEIGHTS
    if today is None:
        today = _dt.date.today()

    id_map = {}
    prepared = []
    for idx, t in enumerate(tasks):
        nid = t.get('id', idx)
        entry = {
            'orig_index': idx,
            'id': nid,
            'title': t.get('title', '').strip(),
            'importance': int(t.get('importance', 5)),
            'estimated_hours': float(t.get('estimated_hours', 1.0)),
            'due_date': t.get('due_date') if (t.get('due_date') is None or isinstance(t.get('due_date'), _dt.date)) else None,
            'dependencies': t.get('dependencies', []) or []
        }

        entry['days_until_due'] = days_until_due(entry['due_date'], today) if entry['due_date'] else None
        prepared.append(entry)
        id_map[nid] = entry

    dep_scores = compute_dependency_scores(tasks)

    raw_urgencies = []
    for p in prepared:
        d = p['days_until_due']
        if d is None:
            u = 0.0
        elif d < 0:
            u = 1.0 + min(0.5, abs(d) / 30.0)  
        elif d == 0:
            u = 0.95
        elif d <= 7:
            u = 0.6 + 0.35 * (1 - (d - 1) / 6.0)  
        elif d <= 30:
            u = 0.2 + 0.4 * (1 - (d - 8) / 22.0)
        else:
            u = 0.05
        raw_urgencies.append(u)

    if raw_urgencies:
        minu = min(raw_urgencies)
        maxu = max(raw_urgencies)
    else:
        minu = 0.0
        maxu = 1.0

    eff_values = [1.0 / (p['estimated_hours'] + 0.01) for p in prepared]  # avoid div by zero
    mine = min(eff_values) if eff_values else 0.0
    maxe = max(eff_values) if eff_values else 1.0

    results = []
    for i, p in enumerate(prepared):
        nid = p['id']
        raw_u = raw_urgencies[i]
        urgency_norm = (raw_u - minu) / (maxu - minu) if maxu != minu else (1.0 if raw_u > 0 else 0.0)

        importance_norm = (p['importance'] - 1) / 9.0  # 1..10 -> 0..1

        eff_raw = eff_values[i]
        effort_norm = (eff_raw - mine) / (maxe - mine) if maxe != mine else (1.0 if eff_raw > 0 else 0.0)

        dependency_norm = dep_scores.get(nid, 0.0)

        score = (weights['urgency'] * urgency_norm +
                 weights['importance'] * importance_norm +
                 weights['effort'] * effort_norm +
                 weights['dependency'] * dependency_norm)

        reasons = []
        if p['days_until_due'] is None:
            reasons.append("No due date (lower urgency)")
        else:
            if p['days_until_due'] < 0:
                reasons.append(f"Past due ({abs(p['days_until_due'])} days overdue) → high urgency")
            elif p['days_until_due'] == 0:
                reasons.append("Due today → high urgency")
            else:
                reasons.append(f"Due in {p['days_until_due']} days")

        reasons.append(f"Importance: {p['importance']}/10")
        reasons.append(f"Estimated hours: {p['estimated_hours']}")
        if dependency_norm > 0:
            reasons.append(f"Blocks {int(round(dependency_norm * 10))} other tasks (dependency score)")
        if effort_norm > 0.7:
            reasons.append("Quick win (low effort)")

        results.append({
            'id': nid,
            'title': p['title'],
            'score': round(float(score), 4),
            'raw': {
                'urgency_norm': round(float(urgency_norm), 4),
                'importance_norm': round(float(importance_norm), 4),
                'effort_norm': round(float(effort_norm), 4),
                'dependency_norm': round(float(dependency_norm), 4),
            },
            'explanation': "; ".join(reasons),
            'metadata': {
                'due_date': p['due_date'].isoformat() if p['due_date'] else None,
                'estimated_hours': p['estimated_hours'],
                'importance': p['importance'],
                'dependencies': p['dependencies']
            }
        })

    results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)
    return results_sorted
