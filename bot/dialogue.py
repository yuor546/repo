from dataclasses import dataclass, field

@dataclass
class DialogueEntry:
    speaker: str
    message: str

@dataclass
class DialogueMemory:
    """Store conversation by user."""

    history: dict[int, list[DialogueEntry]] = field(default_factory=dict)

    def add(self, user_id: int, speaker: str, message: str) -> None:
        self.history.setdefault(user_id, []).append(DialogueEntry(speaker, message))

    def last(self, user_id: int, limit: int = 5) -> str:
        entries = self.history.get(user_id, [])[-limit:]
        return "\n".join(f"{e.speaker}: {e.message}" for e in entries)

    def clear(self, user_id: int) -> None:
        self.history[user_id] = []

    def summarize(self, user_id: int) -> str:
        """Placeholder summarization of conversation history."""
        entries = self.history.get(user_id, [])
        if not entries:
            return ""
        return f"Conversation with {len(entries)} messages."

