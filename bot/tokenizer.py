class SimpleTokenizer:
    """A very basic whitespace tokenizer.

    This tokenizer splits text into tokens based on whitespace. It
    includes a minimal interface that can be replaced with a more
    sophisticated implementation as needed.
    """

    def encode(self, text: str) -> list[str]:
        return text.split()

    def decode(self, tokens: list[str]) -> str:
        return " ".join(tokens)

class CharacterTokenizer:
    """Tokenize text character by character."""

    def encode(self, text: str) -> list[str]:
        return list(text)

    def decode(self, tokens: list[str]) -> str:
        return "".join(tokens)

