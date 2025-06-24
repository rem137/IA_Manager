"""KroniX personality helper."""

from random import choice
from .services import storage

COMMENTS = {
    0: ["{msg}"],
    1: [
        "{msg}. I guess.",
        "Sure, {msg}",
        "{msg}... if you insist",
    ],
    2: [
        "Oh joy, {msg}",
        "Another one? {msg}",
        "{msg}. Whatever.",
    ],
}


def speak(message: str) -> str:
    config = storage.load_config()
    level = config.get("sarcasm", 1)
    options = COMMENTS.get(level, COMMENTS[0])
    return choice(options).format(msg=message)
