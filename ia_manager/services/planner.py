from datetime import date, datetime
from typing import List
from ..models.project import Project


def suggest_tasks(projects: List[Project]) -> List[str]:
    """Return a simple list of task descriptions sorted by priority and importance."""
    pending = []
    for project in projects:
        for task in project.tasks:
            if task.status != "done":
                pending.append((project, task))

    def sort_key(pt):
        p, t = pt
        start = None
        if t.planned_start:
            try:
                start = datetime.fromisoformat(t.planned_start)
            except ValueError:
                start = None
        return (
            start or datetime.max,
            p.priority,
            -t.importance,
        )

    pending.sort(key=sort_key)
    suggestions = [f"{p.name} - {t.name}" for p, t in pending]
    return suggestions
