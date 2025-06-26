from __future__ import annotations
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama
except Exception:  # pragma: no cover - optional dependency
    Llama = None  # type: ignore

from . import memory

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

_llm: Optional["Llama"] = None
_model_name: Optional[str] = None


def available_models() -> list[str]:
    """Return the list of .gguf models found in the models folder."""
    return [p.name for p in MODEL_DIR.glob("*.gguf")]


def load_model(name: str) -> None:
    """Load the given local model if llama_cpp is available."""
    global _llm, _model_name
    if Llama is None:
        _llm = None
        _model_name = None
        return
    path = MODEL_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    _llm = Llama(model_path=str(path))
    _model_name = name


def current_model() -> Optional[str]:
    return _model_name


def ensure_loaded() -> None:
    user = memory.load_user()
    name = user.local_model
    if name and name != _model_name:
        try:
            load_model(name)
        except Exception as exc:  # pragma: no cover - runtime issue
            print(f"[ERROR] Failed to load model {name}: {exc}")
            _llm = None
            _model_name = None


def process_message(message: str) -> Optional[str]:
    """Send the message to the local model and store the returned note."""
    ensure_loaded()
    if _llm is None:
        return None
    user = memory.load_user()
    prompt = (user.local_prompt or "{message}").format(message=message)
    try:
        out = _llm(prompt, max_tokens=64)
    except Exception as exc:  # pragma: no cover - runtime issue
        print(f"[ERROR] Local model inference failed: {exc}")
        return None
    text = out["choices"][0]["text"].strip()
    if text:
        memory.add_fact(text)
    return text
