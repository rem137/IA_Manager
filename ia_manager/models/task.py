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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "estimated": self.estimated,
            "deadline": self.deadline,
            "importance": self.importance,
            "status": self.status,
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
        )
