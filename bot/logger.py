import datetime

class Logger:
    """Simple file logger."""

    def __init__(self, filename: str = "bot.log"):
        self.filename = filename

    def log(self, message: str) -> None:
        timestamp = datetime.datetime.utcnow().isoformat()
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

