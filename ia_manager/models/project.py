from dataclasses import dataclass, field
from typing import List, Optional
from .task import Task

@dataclass
class Project:
    id: int
    name: str
    description: str = ""
    priority: int = 3
    deadline: Optional[str] = None  # YYYY-MM-DD
    status: str = "en cours"
    tasks: List[Task] = field(default_factory=list)

    def progress(self) -> int:
        if not self.tasks:
            return 0
        done = sum(1 for t in self.tasks if t.status == "done")
        return int(done / len(self.tasks) * 100)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline,
            "status": self.status,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @staticmethod
    def from_dict(data: dict) -> "Project":
        tasks = [Task.from_dict(td) for td in data.get("tasks", [])]
        return Project(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            priority=data.get("priority", 3),
            deadline=data.get("deadline"),
            status=data.get("status", "en cours"),
            tasks=tasks,
        )
