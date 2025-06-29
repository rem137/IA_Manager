from dataclasses import dataclass

@dataclass
class User:
    name: str = "User"
    sarcasm: float = 0.3  # 0 (none) to 1 (high)
    context_chars: int = 500  # max characters returned by search

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sarcasm": self.sarcasm,
            "context_chars": self.context_chars,
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            name=data.get("name", "User"),
            sarcasm=data.get("sarcasm", 0.3),
            context_chars=data.get("context_chars", 500),
        )
