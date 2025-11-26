import unittest
from .scoring import score_tasks, detect_circular_dependencies
import datetime


class ScoringTests(unittest.TestCase):


    def test_basic_scoring_order(self):
        tasks = [
            {"id": "a", "title": "low importance", "due_date": None, "estimated_hours": 10, "importance": 2, "dependencies": []},
            {"id": "b", "title": "urgent small", "due_date": (datetime.date.today()).isoformat(), "estimated_hours": 0.5, "importance": 6, "dependencies": []},
        ]
        for t in tasks:
            if t['due_date']:
                t['due_date'] = datetime.datetime.strptime(t['due_date'], '%Y-%m-%d').date()
        res = score_tasks(tasks)
        self.assertEqual(res[0]['id'], 'b')

    def test_dependency_increase_score(self):
        tasks = [
            {"id": 1, "title": "A", "due_date": None, "estimated_hours": 3, "importance": 5, "dependencies": []},
            {"id": 2, "title": "B", "due_date": None, "estimated_hours": 3, "importance": 5, "dependencies": [1]},
            {"id": 3, "title": "C", "due_date": None, "estimated_hours": 3, "importance": 5, "dependencies": [1]}
        ]
        res = score_tasks(tasks)
        ids = [r['id'] for r in res]
        self.assertIn(1, ids[:2])

    def test_cycle_detection(self):
        tasks = [
            {"id": "x", "title": "X", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": ["y"]},
            {"id": "y", "title": "Y", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": ["x"]},
        ]
        cycles = detect_circular_dependencies(tasks)
        self.assertTrue(len(cycles) >= 1)



    def test_overdue_tasks_rank_higher(self):
        """Overdue tasks should get higher priority than future tasks."""
        today = datetime.date.today()
        tasks = [
            {"id": "future", "title": "Future", "due_date": today + datetime.timedelta(days=3),
             "estimated_hours": 3, "importance": 5, "dependencies": []},
            {"id": "overdue", "title": "Overdue", "due_date": today - datetime.timedelta(days=2),
             "estimated_hours": 3, "importance": 5, "dependencies": []}
        ]
        for t in tasks:
            t['due_date'] = t['due_date']

        res = score_tasks(tasks)
        self.assertEqual(res[0]['id'], 'overdue')

    def test_low_effort_quick_win(self):
        """Low-effort tasks should sometimes be prioritized as quick wins."""
        tasks = [
            {"id": "long", "title": "Long Task", "due_date": None, "estimated_hours": 8,
             "importance": 5, "dependencies": []},
            {"id": "quick", "title": "Quick Task", "due_date": None, "estimated_hours": 1,
             "importance": 5, "dependencies": []}
        ]
        res = score_tasks(tasks)
        self.assertEqual(res[0]['id'], 'quick')

    def test_invalid_due_date_handling(self):
        """Tasks with invalid/missing date should not crash the algorithm."""
        tasks = [
            {"id": "valid", "title": "Valid", "due_date": datetime.date.today(),
             "estimated_hours": 2, "importance": 5, "dependencies": []},
            {"id": "invalid", "title": "Invalid", "due_date": "not-a-date",
             "estimated_hours": 2, "importance": 5, "dependencies": []}
        ]

       
        try:
            res = score_tasks(tasks)
            self.assertTrue(len(res) == 2)
        except Exception:
            self.fail("score_tasks() crashed on invalid date input.")

if __name__ == '__main__':
    unittest.main()
