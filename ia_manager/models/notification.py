from dataclasses import dataclass
from typing import Optional

@dataclass
class Notification:
    id: int
    message: str
    action: Optional[str] = None
    status: str = "pending"
