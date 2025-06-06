import pickle
import numpy as np
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, RepeatVector, TimeDistributed

from .memory import Memory

MODEL_PATH = 'autoencoder.h5'
VOCAB_PATH = 'ae_vocab.pkl'
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
    dataX = []
    for i in range(len(text) - SEQ_LEN):
        seq_in = text[i : i + SEQ_LEN]
        dataX.append([stoi.get(ch, 0) for ch in seq_in])
    X = np.array(dataX)
    return X


def main(epochs: int = 10, embed: int = 32, units: int = 64):
    text = load_text()
    if not text:
        print('No training data found.')
        return
    stoi, itos = build_vocab(text)
    X = vectorize(text, stoi)
    vocab_size = len(stoi) + 1

    model = Sequential([
        Embedding(vocab_size, embed, input_length=SEQ_LEN),
        LSTM(units),
        RepeatVector(SEQ_LEN),
        LSTM(units, return_sequences=True),
        TimeDistributed(Dense(vocab_size, activation='softmax')),
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    y = np.expand_dims(X, -1)
    model.fit(X, y, epochs=epochs, batch_size=64)
    model.save(MODEL_PATH)
    with open(VOCAB_PATH, 'wb') as f:
        pickle.dump((stoi, itos), f)
    print('Autoencoder saved to', MODEL_PATH)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--embed', type=int, default=32)
    parser.add_argument('--units', type=int, default=64)
    args = parser.parse_args()
    main(args.epochs, args.embed, args.units)
