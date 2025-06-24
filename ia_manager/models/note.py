from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Note:
    id: int
    text: str
    keywords: List[str] = field(default_factory=list)
    project: Optional[int] = None
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "keywords": self.keywords,
            "project": self.project,
            "created": self.created,
        }

    @staticmethod
    def from_dict(data: dict) -> "Note":
        return Note(
            id=data["id"],
            text=data["text"],
            keywords=data.get("keywords", []),
            project=data.get("project"),
            created=data.get("created", datetime.utcnow().isoformat()),
        )
