from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Note:
    id: int
    text: str
    tags: List[str] = field(default_factory=list)
    project_id: Optional[int] = None
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "tags": self.tags,
            "project_id": self.project_id,
            "created": self.created,
        }

    @staticmethod
    def from_dict(data: dict) -> "Note":
        return Note(
            id=data["id"],
            text=data.get("text", ""),
            tags=list(data.get("tags", [])),
            project_id=data.get("project_id"),
            created=data.get("created", datetime.utcnow().isoformat()),
        )
