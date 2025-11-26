import datetime
from typing import Tuple, Dict, Any
import json

def validate_task_dict(t: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single task dictionary. Returns (is_valid, error_message).
    Expected keys: title (str), due_date (YYYY-MM-DD optional), estimated_hours (number), importance (1-10), dependencies (list of ids)
    """
    if not isinstance(t, dict):
        return False, "Task must be an object"
    if 'title' not in t or not isinstance(t['title'], str) or not t['title'].strip():
        return False, "Missing or invalid 'title'"
    if 'importance' in t:
        try:
            imp = int(t['importance'])
            if not (1 <= imp <= 10):
                return False, "'importance' must be 1-10"
        except Exception:
            return False, "'importance' must be integer 1-10"
    else:
        t['importance'] = 5
    if 'estimated_hours' in t:
        try:
            t['estimated_hours'] = float(t['estimated_hours'])
            if t['estimated_hours'] < 0:
                return False, "'estimated_hours' must be non-negative"
        except Exception:
            return False, "'estimated_hours' must be a number"
    else:
        t['estimated_hours'] = 1.0
    if 'due_date' in t and t['due_date'] is not None:
        try:
            if isinstance(t['due_date'], (int, float)):
                t['due_date'] = datetime.date.fromtimestamp(t['due_date'])
            elif isinstance(t['due_date'], str):
                t['due_date'] = datetime.datetime.strptime(t['due_date'], '%Y-%m-%d').date()
            elif isinstance(t['due_date'], datetime.date):
                pass
            else:
                return False, "'due_date' must be YYYY-MM-DD or null"
        except Exception:
            return False, "'due_date' must be YYYY-MM-DD"
    else:
        t['due_date'] = None
    if 'dependencies' in t:
        if not isinstance(t['dependencies'], list):
            return False, "'dependencies' must be a list of task ids"
    else:
        t['dependencies'] = []
    return True, ""
