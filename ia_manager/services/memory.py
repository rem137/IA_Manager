import json
from pathlib import Path
from .storage import DATA_DIR

USER_FILE = DATA_DIR / "memory.json"
NOTES_FILE = DATA_DIR / "notes.json"


def load_user() -> dict:
    if not USER_FILE.exists():
        return {"name": "User", "sarcasm": 1}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user(user: dict):
    USER_FILE.parent.mkdir(exist_ok=True)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user, f, indent=2, ensure_ascii=False)


def load_notes() -> list:
    if not NOTES_FILE.exists():
        return []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_notes(notes: list):
    NOTES_FILE.parent.mkdir(exist_ok=True)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
