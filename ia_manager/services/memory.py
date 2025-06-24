import json
from pathlib import Path
from typing import List
from datetime import datetime

from ..models.note import Note
from ..models.user import User

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MEMORY_FILE = DATA_DIR / "memory.json"
PERSONALITY_FILE = DATA_DIR / "personality.json"


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)


def load_memory() -> dict:
    _ensure_dirs()
    if not MEMORY_FILE.exists():
        return {"notes": [], "session_note": ""}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(data: dict):
    _ensure_dirs()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_notes() -> List[Note]:
    mem = load_memory()
    return [Note.from_dict(n) for n in mem.get("notes", [])]


def save_notes(notes: List[Note]):
    mem = load_memory()
    mem["notes"] = [n.to_dict() for n in notes]
    save_memory(mem)


def load_custom_session_note() -> str:
    mem = load_memory()
    return mem.get("session_note", "")


def save_custom_session_note(text: str):
    mem = load_memory()
    mem["session_note"] = text
    save_memory(mem)


def load_user() -> User:
    if not PERSONALITY_FILE.exists():
        return User()
    with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return User.from_dict(data)


def save_user(user: User):
    _ensure_dirs()
    with open(PERSONALITY_FILE, "w", encoding="utf-8") as f:
        json.dump(user.to_dict(), f, indent=2, ensure_ascii=False)


def generate_session_note(projects: List, notes: List[Note], user: User) -> str:
    """Return a short contextual note (max 500 chars)."""
    upcoming = []
    today = datetime.utcnow().date()
    for p in projects:
        for t in p.tasks:
            if t.status == "done" or not t.deadline:
                continue
            try:
                d = datetime.fromisoformat(t.deadline)
            except ValueError:
                continue
            if 0 <= (d.date() - today).days <= 7:
                upcoming.append(f"{p.name}:{t.name}({d.date()})")
    msg = f"Hello {user.name}. "
    if upcoming:
        msg += "Upcoming: " + ", ".join(upcoming[:3]) + ". "
    if notes:
        msg += "Last note: " + notes[-1].text[:40] + ". "
    if not upcoming and not notes:
        msg += "Nothing urgent. "
    if user.sarcasm >= 0.7:
        msg += "Try not to procrastinate."
    elif user.sarcasm >= 0.3:
        msg += "Let's keep moving."
    return msg[:500]
