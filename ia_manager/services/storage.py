import json
from pathlib import Path
from typing import List
from ..models.project import Project

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"
CONFIG_FILE = DATA_DIR / "config.json"
LOG_FILE = DATA_DIR / "log.txt"
DOCS_DIR = DATA_DIR / "docs"
IMPROVEMENTS_FILE = DATA_DIR / "improvements.json"

DATA_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)


def load_projects() -> List[Project]:
    if not PROJECTS_FILE.exists():
        return []
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Project.from_dict(d) for d in data]


def save_projects(projects: List[Project]):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in projects], f, indent=2, ensure_ascii=False)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"availability": {}}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_improvements() -> list:
    if not IMPROVEMENTS_FILE.exists():
        return []
    with open(IMPROVEMENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_improvements(items: list):
    with open(IMPROVEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
