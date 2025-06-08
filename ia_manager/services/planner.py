from datetime import date
from typing import List
from ..models.project import Project


def suggest_tasks(projects: List[Project]) -> List[str]:
    """Return a simple list of task descriptions sorted by priority and importance."""
    pending = []
    for project in projects:
        for task in project.tasks:
            if task.status != "done":
                pending.append((project, task))

    pending.sort(key=lambda pt: (pt[0].priority, -pt[1].importance))
    suggestions = [f"{p.name} - {t.name}" for p, t in pending]
    return suggestions
