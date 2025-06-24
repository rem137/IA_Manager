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
        return {"notes": [], "session_note": "", "history": []}
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


def load_history() -> list:
    mem = load_memory()
    return list(mem.get("history", []))


def save_history(history: list):
    mem = load_memory()
    mem["history"] = history
    save_memory(mem)


def append_history(role: str, text: str):
    history = load_history()
    history.append({"role": role, "text": text, "ts": datetime.utcnow().isoformat()})
    save_history(history)


def search_history(query: str, limit: int = 3) -> list:
    """Return recent messages containing the query."""
    history = load_history()
    q = query.lower()
    results = []
    for item in reversed(history):
        if q in item.get("text", "").lower():
            results.append(item)
        if len(results) >= limit:
            break
    return list(reversed(results))


def search_notes(query: str, notes: List[Note] | None = None, limit: int = 3) -> list[Note]:
    if notes is None:
        notes = load_notes()
    q = query.lower()
    results: list[Note] = []
    for n in reversed(notes):
        if q in n.text.lower() or any(q in t.lower() for t in n.tags):
            results.append(n)
        if len(results) >= limit:
            break
    return list(reversed(results))


def get_context(query: str, max_chars: int = 300) -> str:
    """Return a short summary of history and notes related to the query."""
    notes = search_notes(query)
    hist = search_history(query)
    parts = []
    if notes:
        parts.append("Notes: " + "; ".join(n.text for n in notes))
    if hist:
        parts.append("Messages: " + "; ".join(h["text"] for h in hist))
    ctx = " ".join(parts)
    return ctx[:max_chars]
