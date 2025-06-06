import pickle
import argparse
import numpy as np
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Embedding, LSTM, RepeatVector, TimeDistributed, Dense
from .memory import Memory

MODEL_PATH = 'autoencoder_model.h5'
VOCAB_PATH = 'autoencoder_vocab.pkl'
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
    return np.array(dataX)


def main(epochs: int = 5, embedding: int = 32, hidden: int = 64):
    text = load_text()
    if not text:
        print('No training data found.')
        return
    stoi, itos = build_vocab(text)
    X = vectorize(text, stoi)
    vocab_size = len(stoi) + 1

    model = Sequential([
        Embedding(vocab_size, embedding, input_length=SEQ_LEN),
        LSTM(hidden),
        RepeatVector(SEQ_LEN),
        LSTM(hidden, return_sequences=True),
        TimeDistributed(Dense(vocab_size, activation='softmax')),
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    model.fit(X, X, epochs=epochs, batch_size=64)
    model.save(MODEL_PATH)
    with open(VOCAB_PATH, 'wb') as f:
        pickle.dump((stoi, itos), f)
    print('Autoencoder model saved to', MODEL_PATH)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train an autoencoder model')
    parser.add_argument('--epochs', type=int, default=5,
                        help='number of training epochs (default: 5)')
    parser.add_argument('--embedding', type=int, default=32,
                        help='embedding dimension size')
    parser.add_argument('--hidden', type=int, default=64,
                        help='hidden layer size')
    args = parser.parse_args()
    main(epochs=args.epochs, embedding=args.embedding, hidden=args.hidden)
