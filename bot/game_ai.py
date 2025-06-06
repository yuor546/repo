import os
import pickle
import random
import numpy as np


class GameAI:
    """Simple game AI with optional Q-learning."""

    def __init__(self, q_table_path: str = "q_table.pkl"):
        self.state = {}
        self.q_table_path = q_table_path
        self.q_table = {}
        if os.path.isfile(q_table_path):
            self.load_q_table(q_table_path)

    def load_q_table(self, path: str | None = None) -> None:
        """Load a Q-learning table from disk."""
        use_path = path or self.q_table_path
        try:
            with open(use_path, "rb") as f:
                self.q_table = pickle.load(f)
        except Exception:
            self.q_table = {}

    def q_move(self, board: list[str]) -> int:
        """Choose a move for tic-tac-toe using the Q-table."""
        key = "".join(board)
        moves = [i for i, c in enumerate(board) if c == " "]
        if not moves:
            return -1
        qvals = self.q_table.get(key)
        if qvals is None:
            return random.choice(moves)
        best = int(np.argmax(qvals))
        return best if best in moves else random.choice(moves)

    async def decide_action(self, game_state) -> str:
        board = game_state.get("board")
        if board:
            move = self.q_move(board)
            return str(move)
        return "move_forward"

    # Placeholders for advanced integrations
    def connect_necto(self):
        """Stub for connecting to a Necto client."""
        pass

    def connect_baritone(self):
        """Stub for connecting to a Baritone client."""
        pass

