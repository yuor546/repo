import pickle
import argparse
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
import numpy as np
from .memory import Memory

MODEL_PATH = 'lstm_model.h5'
VOCAB_PATH = 'lstm_vocab.pkl'
SEQ_LEN = 40


def load_text() -> str:
    mem = Memory()
    pairs = list(mem.training().items())
    mem.close()
    text = '\n'.join([p + ' ' + r for p, r in pairs])
    return text


def build_vocab(text: str):
    chars = sorted(set(text))
    stoi = {ch: i + 1 for i, ch in enumerate(chars)}  # 0 reserved for padding
    itos = {i + 1: ch for i, ch in enumerate(chars)}
    return stoi, itos


def vectorize(text: str, stoi: dict[str, int]):
    dataX, dataY = [], []
    for i in range(len(text) - SEQ_LEN):
        seq_in = text[i : i + SEQ_LEN]
        seq_out = text[i + SEQ_LEN]
        dataX.append([stoi.get(ch, 0) for ch in seq_in])
        dataY.append(stoi.get(seq_out, 0))
    return np.array(dataX), np.array(dataY)


def main(epochs: int = 5, embedding: int = 32, units: int = 64):
    text = load_text()
    if not text:
        print('No training data found.')
        return
    stoi, itos = build_vocab(text)
    X, y = vectorize(text, stoi)
    vocab_size = len(stoi) + 1

    model = Sequential([
        Embedding(vocab_size, embedding, input_length=SEQ_LEN),
        LSTM(units),
        Dense(vocab_size, activation='softmax'),
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    model.fit(X, y, epochs=epochs, batch_size=64)
    model.save(MODEL_PATH)
    with open(VOCAB_PATH, 'wb') as f:
        pickle.dump((stoi, itos), f)
    print('Model saved to', MODEL_PATH)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train the LSTM model')
    parser.add_argument('--epochs', type=int, default=5,
                        help='number of training epochs (default: 5)')
    parser.add_argument('--embedding', type=int, default=32,
                        help='embedding dimension size')
    parser.add_argument('--units', type=int, default=64,
                        help='number of LSTM units')
    args = parser.parse_args()
    main(epochs=args.epochs, embedding=args.embedding, units=args.units)
