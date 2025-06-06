import pickle
import numpy as np
from tensorflow import keras

class LSTMModel:
    """Character-level LSTM language model."""
    def __init__(self, model_path: str, stoi: dict[str, int], itos: dict[int, str], seq_len: int = 40):
        self.model = keras.models.load_model(model_path)
        self.stoi = stoi
        self.itos = itos
        self.seq_len = seq_len

    def _encode(self, text: str) -> list[int]:
        return [self.stoi.get(ch, 0) for ch in text]

    def _decode_token(self, idx: int) -> str:
        return self.itos.get(idx, '')

    def generate(self, prompt: str, max_tokens: int = 20) -> str:
        seed = prompt[-self.seq_len:]
        encoded = self._encode(seed.rjust(self.seq_len))
        out = list(seed)
        for _ in range(max_tokens):
            x = np.array([encoded])
            preds = self.model.predict(x, verbose=0)[0]
            idx = int(np.argmax(preds))
            ch = self._decode_token(idx)
            out.append(ch)
            encoded = encoded[1:] + [idx]
        return ''.join(out)
