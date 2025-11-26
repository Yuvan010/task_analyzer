# 📘 Smart Task Analyzer

The Smart Task Analyzer is an intelligent task-prioritization system built using Django (Backend) and HTML/CSS/JavaScript (Frontend). It analyzes tasks based on urgency, importance, effort, and dependencies to determine what the user should work on first. This project was built as part of the Singularium Internship Technical Assessment.

## 🚀 Project Overview

This system allows users to input tasks (via form or JSON), processes them using an intelligent scoring algorithm, and returns:

- A priority score for each task
- A sorted list of tasks
- Top 3 task suggestions
- Detailed scoring explanations
- Multiple sorting strategies
- An Eisenhower Matrix visualization (Bonus Feature)

The app is fully interactive, supports bulk JSON input, and updates dynamically each time the user analyzes new tasks.

**GitHub Repository:** [Yuvan010/task_analyzer](https://github.com/Yuvan010/task_analyzer)

## 🧠 Scoring Algorithm (Core Logic)

Each task receives a combined weighted score based on four major factors:

### 1. Urgency

Urgency is calculated from the due date.

- If the task is overdue, it receives the highest urgency.
- Tasks due within 0–2 days get medium urgency.
- Tasks due later get low urgency.

**Formula:**
```
days_remaining = (due_date – today).days
```

- Overdue → strong positive urgency
- 0–2 days → medium
- 2+ days → low

### 2. Importance (1–10 scale)

Higher importance significantly increases the final score.

### 3. Effort (Estimated Hours)

- Low-effort tasks get a "quick-win bonus."
- High-effort tasks get a small penalty.
- This helps bring small tasks forward.

### 4. Dependencies

- Tasks that other tasks depend on receive extra priority.
- This ensures blocking tasks appear earlier.
- Dependency weight = number of tasks that depend on this task

### Weighted Final Score (Simplified Form)

```
score = (importance × W1) + (urgency × W2) + (quick_win_bonus × W3) + (dependency_weight × W4)
```

Weights are adjusted depending on the user's selected sorting strategy.

### Algorithm Explanation

The priority scoring algorithm works by combining multiple factors to determine which tasks should be completed first. The algorithm considers:

- **Urgency weighting**: Overdue tasks and tasks with approaching deadlines receive significantly higher scores to ensure time-sensitive work is prioritized
- **Importance scaling**: User-defined importance (1-10) is multiplied by a weight factor to ensure critical tasks rise to the top
- **Quick-win bonus**: Tasks requiring less than 2 hours of effort receive a bonus multiplier, encouraging productivity through small completions
- **Dependency chaining**: Tasks that block other tasks (dependencies) receive priority boosts proportional to how many tasks depend on them

The algorithm adapts based on the selected sorting strategy, adjusting the weight coefficients (W1-W4) to emphasize different factors. For example, the "Deadline Driven" strategy increases urgency weights while reducing importance weights, whereas "High Impact" does the opposite.

## 🌐 API Endpoints

### `POST /api/tasks/analyze/`

Accepts a list of tasks in JSON format and returns:

- Calculated scores
- Sorted tasks
- Explanation text
- Dependency cycle detection

### `GET /api/tasks/suggest/`

Returns the top 3 recommended tasks with explanation text.

## ⚡ Sorting Strategies (Frontend)

Users can choose between four prioritization strategies:

- **Fastest Wins** – Prefers low-effort tasks
- **High Impact** – Importance dominates scoring
- **Deadline Driven** – Pure urgency-based
- **Smart Balance** – The main hybrid algorithm combining all factors

Each strategy dynamically adjusts the scoring weights.

## 🖥 Frontend UI Features

- Task creation form
- Bulk JSON input box
- Analyze Tasks button
- Sorted results with:
  - Score
  - Color-coded priority level (High / Medium / Low)
  - Explanation of scoring
- Responsive updates
- Error validation (invalid JSON, missing fields)
- Eisenhower Matrix visualization (bonus feature)

## 🎁 Bonus Challenges Completed

### 1. Comprehensive Unit Tests

Created a suite of tests that cover:

- Basic scoring order
- Dependency-based priority changes
- Circular dependency detection
- Overdue tasks placed above future tasks
- Quick-win logic for low-effort tasks
- Handling invalid date formats safely

These tests validate the scoring system and ensure all logic remains consistent.

**Running the tests:**
```bash
python manage.py test
```

Expected output:
```
Found 6 tests.
......
OK
```

### 2. Eisenhower Matrix Visualization

A complete 2×2 grid that categorizes tasks into:

- Urgent & Important
- Not Urgent & Important
- Urgent & Not Important
- Not Urgent & Not Important

This matrix updates live whenever tasks are analyzed and provides a visual prioritization tool beyond just scores.

## 📁 Project Structure

```
backend/
├── manage.py
└── task_analyzer/
    └── tasks/
        ├── scoring.py
        ├── views.py
        ├── urls.py
        ├── serializers.py
        ├── models.py
        └── tests.py (includes bonus unit tests)

frontend/
├── index.html
├── styles.css
└── script.js
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yuvan010/task_analyzer.git
   cd task_analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Run the backend:**
   ```bash
   python manage.py runserver
   ```

5. **Open the frontend:**
   Open `frontend/index.html` in your browser or navigate to `http://localhost:8000` if serving through Django.

## 🧪 Running Tests

Run:
```bash
python manage.py test
```

Expected result:
```
Found 6 tests.
......
OK
```

## ⏱ Time Breakdown

Approximate time spent on each section:

- **Scoring Algorithm:** 1 hour
- **Backend API:** 40 minutes
- **Frontend UI Development:** 1 hour
- **Sorting Strategy Logic:** 20 minutes
- **Bonus – Unit Tests:** 45 minutes
- **Bonus – Eisenhower Matrix:** 35 minutes

**Total Development Time:** ~4 hours 20 minutes

## 🎯 Design Decisions

### Why Django for Backend?
Django was chosen for its robust ORM, built-in REST capabilities, and rapid development features. The framework provides excellent structure for organizing the scoring logic and API endpoints.

### Scoring Algorithm Trade-offs
- **Multi-factor approach:** Rather than using a single metric, the algorithm combines urgency, importance, effort, and dependencies to provide more nuanced prioritization
- **Weight-based flexibility:** Different sorting strategies allow users to adapt the algorithm to their work style without changing the core logic
- **Quick-win bonus:** This design decision encourages momentum by surfacing easy completions, which psychological research shows improves productivity

### Frontend Architecture
A vanilla JavaScript approach was used to keep the frontend lightweight and dependency-free. The UI updates dynamically using DOM manipulation, making it responsive without requiring a full framework.

### Dependency Handling
The system detects circular dependencies to prevent infinite loops and provides clear error messages. Tasks are treated as a directed acyclic graph (DAG) where blocking tasks naturally rise in priority.

## 🔮 Future Improvements

- Authentication & user accounts
- Storing tasks in a database for persistence
- Drag-and-drop task editing
- Holiday/weekend aware urgency logic
- Graph visualization of task dependencies
- Mobile-responsive redesign
- Adaptive AI-based scoring (learning user preferences)

## 🏁 Conclusion

The Smart Task Analyzer is a complete productivity-focused system combining strong backend logic, clean API architecture, dynamic frontend interaction, and additional bonus enhancements like advanced tests and the Eisenhower Matrix. It demonstrates algorithmic thinking, UI/UX implementation, and problem-solving depth suitable for real-world software engineering challenges.
