import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .serializers import validate_task_dict
from .scoring import score_tasks, detect_circular_dependencies
import datetime

@csrf_exempt
def analyze_tasks(request):
    
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({'error': 'POST required'}), content_type='application/json')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON'}), content_type='application/json')

    if not isinstance(payload, list):
        return HttpResponseBadRequest(json.dumps({'error': 'Expected a JSON array of tasks'}), content_type='application/json')

    validated = []
    errors = []
    for i, t in enumerate(payload):
        ok, msg = validate_task_dict(t)
        if not ok:
            errors.append({'index': i, 'error': msg})
        else:
            if 'id' not in t:
                t['id'] = i
            validated.append(t)

    if errors:
        return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)

    cycles = detect_circular_dependencies(validated)
    cycle_info = cycles if cycles else []

    results = score_tasks(validated, today=datetime.date.today())

    response = {
        'results': results,
        'cycles': cycle_info
    }
    return JsonResponse(response, safe=False)

def parse_tasks_from_query(q):
    
    import json
    if not q:
        return None, "No tasks provided in query parameter 'tasks'"
    try:
        tasks = json.loads(q)
        if not isinstance(tasks, list):
            return None, "Query 'tasks' must be JSON array"
        return tasks, None
    except Exception:
        return None, "Invalid JSON in 'tasks' query"

def explain_top3(results):
   
    out = []
    for r in results[:3]:
        out.append({
            'id': r['id'],
            'title': r['title'],
            'score': r['score'],
            'explanation': r['explanation'],
            'metadata': r['metadata']
        })
    return out

def suggest_tasks(request):
    
    if request.method != 'GET':
        return HttpResponseBadRequest(json.dumps({'error': 'GET required'}), content_type='application/json')

    tasks_q = request.GET.get('tasks')
    tasks, err = parse_tasks_from_query(tasks_q)
    if err:
        return JsonResponse({'error': err}, status=400)

    
    validated = []
    errors = []
    from .serializers import validate_task_dict
    for i, t in enumerate(tasks):
        ok, msg = validate_task_dict(t)
        if not ok:
            errors.append({'index': i, 'error': msg})
        else:
            if 'id' not in t:
                t['id'] = i
            validated.append(t)
    if errors:
        return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)

    cycles = detect_circular_dependencies(validated)

    results = score_tasks(validated)

    top3 = explain_top3(results)

    response = {
        'top3': top3,
        'cycles': cycles
    }
    return JsonResponse(response, safe=False)
