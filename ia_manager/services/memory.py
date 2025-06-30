import json
from pathlib import Path
from typing import List
from datetime import datetime
import re

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


def add_internal_note(text: str):
    """Store a note for the assistant only."""
    notes = load_notes()
    note_id = max([n.id for n in notes], default=0) + 1
    notes.append(Note(id=note_id, text=text, internal=True))
    save_notes(notes)


def add_fact(text: str):
    """Store an important fact visible in search results."""
    notes = load_notes()
    note_id = max([n.id for n in notes], default=0) + 1
    notes.append(Note(id=note_id, text=text))
    save_notes(notes)


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



def _score(text: str, tokens: list[str]) -> float:
    words = set(re.findall(r"\w+", text.lower()))
    if not words:
        return 0.0
    matched = sum(1 for t in tokens if t in words)
    return matched / len(tokens) if tokens else 0.0


def search_history(query: str, limit: int = 3) -> list:
    """Return most relevant past messages."""
    history = load_history()
    tokens = re.findall(r"\w+", query.lower())
    scored = []
    for item in history:
        score = _score(item.get("text", ""), tokens)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _score_val, item in scored[:limit]]


def search_notes(
    query: str,
    notes: List[Note] | None = None,
    limit: int = 3,
    include_internal: bool = False,
) -> list[Note]:
    if notes is None:
        notes = load_notes()
    tokens = re.findall(r"\w+", query.lower())
    scored: list[tuple[float, Note]] = []
    for n in notes:
        if not include_internal and n.internal:
            continue
        combined = n.text + " " + " ".join(n.tags)
        score = _score(combined, tokens)
        if score:
            scored.append((score, n))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [n for _score_val, n in scored[:limit]]


def get_context(query: str, max_chars: int | None = None, include_internal: bool = False) -> str:
    """Return a short summary of notes related to the query."""
    if max_chars is None:
        max_chars = load_user().context_chars
    notes = search_notes(query, include_internal=include_internal)
    parts = []
    if notes:
        parts.append("Notes: " + "; ".join(n.text for n in notes))
    ctx = " ".join(parts)
    return ctx[:max_chars]


def related_facts(query: str, limit: int = 3) -> list[str]:
    """Return short texts from notes related to the query."""
    notes = search_notes(query, limit=limit, include_internal=True)
    return [n.text for n in notes]


def last_messages(count: int = 5) -> list[str]:
    """Return the most recent chat messages formatted with roles."""
    history = load_history()
    messages = []
    for item in history[-count:]:
        role = "Utilisateur" if item.get("role") == "user" else "IA"
        messages.append(f"{role} : {item.get('text', '')}")
    return messages
