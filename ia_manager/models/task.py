from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Task:
    id: int
    name: str
    estimated: Optional[int] = None  # in hours
    deadline: Optional[str] = None  # YYYY-MM-DD
    importance: int = 3
    status: str = "todo"  # todo, planned, in_progress, done
    description: str = ""
    started: Optional[str] = None  # ISO timestamp when timer started
    time_spent: int = 0  # seconds spent on task
    planned_start: Optional[str] = None  # ISO timestamp planned start
    planned_end: Optional[str] = None    # ISO timestamp planned end
    planned_hours: Optional[float] = None

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
            "planned_start": self.planned_start,
            "planned_end": self.planned_end,
            "planned_hours": self.planned_hours,
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
            planned_start=data.get("planned_start"),
            planned_end=data.get("planned_end"),
            planned_hours=data.get("planned_hours"),
        )
