from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    id: int
    name: str
    estimated: Optional[int] = None  # in hours
    deadline: Optional[str] = None  # YYYY-MM-DD
    importance: int = 3
    status: str = "todo"  # todo, done
    description: str = ""
    started: Optional[str] = None  # ISO timestamp when timer started
    time_spent: int = 0  # seconds spent on task

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "estimated": self.estimated,
            "deadline": self.deadline,
            "importance": self.importance,
            "status": self.status,
            "description": self.description,
            "started": self.started,
            "time_spent": self.time_spent,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        return Task(
            id=data["id"],
            name=data["name"],
            estimated=data.get("estimated"),
            deadline=data.get("deadline"),
            importance=data.get("importance", 3),
            status=data.get("status", "todo"),
            description=data.get("description", ""),
            started=data.get("started"),
            time_spent=data.get("time_spent", 0),
        )
