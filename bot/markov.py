import pickle
from collections import defaultdict

class MarkovChain:
    """Very small word-level Markov chain model."""

    def __init__(self, tokenizer=None):
        self.model = defaultdict(lambda: defaultdict(int))
        self.tokenizer = tokenizer

    def train_on_text(self, text: str):
        tokens = self.tokenizer.encode(text)
        if len(tokens) < 3:
            return
        for a, b, c in zip(tokens, tokens[1:], tokens[2:]):
            self.model[(a, b)][c] += 1

    def train_pairs(self, pairs: list[tuple[str, str]]):
        for p, r in pairs:
            self.train_on_text(p + " " + r)

    def generate(self, prompt: str, max_tokens: int = 20) -> str:
        tokens = self.tokenizer.encode(prompt)
        if len(tokens) < 2:
            tokens = ["", *tokens]
        out = tokens[:]
        for _ in range(max_tokens):
            key = tuple(out[-2:])
            next_words = self.model.get(key)
            if not next_words:
                break
            # Choose the most common next word
            next_word = max(next_words.items(), key=lambda x: x[1])[0]
            out.append(next_word)
        return self.tokenizer.decode(out)

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(dict(self.model), f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = defaultdict(lambda: defaultdict(int), data)
