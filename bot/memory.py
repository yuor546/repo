import shelve
class Memory:
    """Persistent memory storage for conversation history and training data."""

    def __init__(self, filename: str = "bot_memory"):
        self.db = shelve.open(filename, writeback=True)
        if "history" not in self.db:
            self.db["history"] = {}
        if "training" not in self.db:
            self.db["training"] = {}
        if "cookies" not in self.db:
            self.db["cookies"] = {}
        if "rewards" not in self.db:
            self.db["rewards"] = {}
        if "voices" not in self.db:
            self.db["voices"] = {}

    def close(self):
        self.db.close()

    def history(self, channel_id: int) -> str:
        return self.db["history"].get(channel_id, "")

    def update_history(self, channel_id: int, entry: str) -> None:
        hist = self.db["history"].get(channel_id, "") + entry
        self.db["history"][channel_id] = hist
        self.db.sync()

    def clear_history(self, channel_id: int) -> None:
        if channel_id in self.db["history"]:
            self.db["history"][channel_id] = ""
            self.db.sync()

    def training(self) -> dict:
        return self.db["training"]

    def add_training(self, prompt: str, response: str) -> None:
        self.db["training"][prompt] = response
        self.db.sync()

    # Cookie and reward helpers
    def cookies(self, guild_id: int) -> int:
        return self.db["cookies"].get(guild_id, 0)

    def add_cookies(self, guild_id: int, amount: int) -> None:
        self.db["cookies"][guild_id] = self.cookies(guild_id) + amount
        self.db.sync()

    def rewards(self, user_id: int) -> int:
        return self.db["rewards"].get(user_id, 0)

    def add_reward(self, user_id: int, amount: int) -> None:
        self.db["rewards"][user_id] = self.rewards(user_id) + amount
        self.db.sync()

    # Voice recognition helpers
    def voice(self, user_id: int):
        return self.db["voices"].get(user_id)

    def set_voice(self, user_id: int, features) -> None:
        self.db["voices"][user_id] = features
        self.db.sync()

