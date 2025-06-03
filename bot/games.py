import random
from dataclasses import dataclass

@dataclass
class TicTacToeState:
    board: list[str]
    players: list[int]
    turn: int = 0

    def display(self) -> str:
        return (
            "|".join(self.board[0:3])
            + "\n"
            + "|".join(self.board[3:6])
            + "\n"
            + "|".join(self.board[6:9])
        )

class TicTacToeGame:
    def __init__(self, player1: int, player2: int):
        self.state = TicTacToeState(board=[" "] * 9, players=[player1, player2])

    def make_move(self, player_id: int, position: int) -> tuple[str | None, str | None]:
        if self.state.players[self.state.turn] != player_id:
            return None, "It's not your turn."
        if not 0 <= position <= 8 or self.state.board[position] != " ":
            return None, "Invalid move."
        mark = "X" if self.state.turn == 0 else "O"
        self.state.board[position] = mark
        self.state.turn = 1 - self.state.turn
        winner = self.check_winner()
        board_display = self.state.display()
        if winner:
            return f"```\n{board_display}\n```\n{winner} wins!", "END"
        if " " not in self.state.board:
            return f"```\n{board_display}\n```\nIt's a draw!", "END"
        return f"```\n{board_display}\n```", None

    def check_winner(self) -> str | None:
        b = self.state.board
        wins = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b1, c in wins:
            if b[a] == b[b1] == b[c] != " ":
                return b[a]
        return None

@dataclass
class RPSState:
    scores: dict[int, int]
    rounds: int
    current_round: int = 0

class RockPaperScissorsGame:
    CHOICES = ["rock", "paper", "scissors"]

    def __init__(self, player1: int, player2: int, rounds: int = 3):
        self.state = RPSState(scores={player1: 0, player2: 0}, rounds=rounds)
        self.players = [player1, player2]

    def play_round(self, p1_choice: str, p2_choice: str) -> str:
        p1_choice = p1_choice.lower()
        p2_choice = p2_choice.lower()
        if p1_choice not in self.CHOICES or p2_choice not in self.CHOICES:
            return "Invalid choice. Use rock, paper, or scissors."
        result = self.determine_winner(p1_choice, p2_choice)
        self.state.current_round += 1
        if result == 0:
            outcome = "Tie!"
        elif result == 1:
            self.state.scores[self.players[0]] += 1
            outcome = "Player 1 wins the round!"
        else:
            self.state.scores[self.players[1]] += 1
            outcome = "Player 2 wins the round!"
        if self.state.current_round >= self.state.rounds:
            p1_score = self.state.scores[self.players[0]]
            p2_score = self.state.scores[self.players[1]]
            if p1_score == p2_score:
                outcome += " Final result: Draw!"
            elif p1_score > p2_score:
                outcome += " Final result: Player 1 wins!"
            else:
                outcome += " Final result: Player 2 wins!"
        return outcome

    @staticmethod
    def determine_winner(c1: str, c2: str) -> int:
        if c1 == c2:
            return 0
        wins = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper",
        }
        return 1 if wins[c1] == c2 else 2


@dataclass
class GuessNumberState:
    secret: int
    attempts: int
    max_attempts: int

class GuessNumberGame:
    """Simple number guessing game."""

    def __init__(self, max_attempts: int = 5):
        secret = random.randint(1, 100)
        self.state = GuessNumberState(secret=secret, attempts=0, max_attempts=max_attempts)

    def guess(self, number: int) -> str:
        self.state.attempts += 1
        if number == self.state.secret:
            return "Correct! You've guessed the number."
        if self.state.attempts >= self.state.max_attempts:
            return f"Out of attempts! The number was {self.state.secret}."
        hint = "higher" if number < self.state.secret else "lower"
        return f"Try {hint}!"


@dataclass
class HangmanState:
    word: str
    guesses: set[str]
    attempts: int
    max_attempts: int

    def display(self) -> str:
        return ' '.join(c if c in self.guesses else '_' for c in self.word)

class HangmanGame:
    WORDS = ['python', 'discord', 'hangman', 'assistant']

    def __init__(self, max_attempts: int = 6):
        word = random.choice(self.WORDS)
        self.state = HangmanState(word=word, guesses=set(), attempts=0, max_attempts=max_attempts)

    def guess(self, letter: str) -> str:
        letter = letter.lower()
        if letter in self.state.guesses:
            return 'Already guessed.'
        self.state.guesses.add(letter)
        if letter not in self.state.word:
            self.state.attempts += 1
        if self.state.attempts >= self.state.max_attempts:
            return f'Game over! The word was {self.state.word}.'
        if all(c in self.state.guesses for c in self.state.word):
            return f'You win! The word was {self.state.word}.'
        return self.state.display()

