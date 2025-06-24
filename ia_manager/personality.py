import random
from .services import memory
from .utils import color, Fore


def _prefix() -> str:
    user = memory.load_user()
    level = user.get("sarcasm", 1)
    if level <= 0:
        return ""
    mild = ["Alright,", "Okay,", "Sure,", "Fine,"]
    strong = [
        "I guess I'll handle that.",
        "Because that's exactly what I wanted to do.",
        "As if I had a choice.",
    ]
    choices = mild + strong if level >= 2 else mild
    return random.choice(choices) + " "


def say(message: str):
    print(color(_prefix() + message, Fore.MAGENTA))


def format(message: str) -> str:
    return color(_prefix() + message, Fore.MAGENTA)
