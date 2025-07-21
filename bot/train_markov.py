from .tokenizer import SimpleTokenizer
from .memory import Memory
from .markov import MarkovChain

MODEL_PATH = 'markov_model.pkl'

def main():
    mem = Memory()
    tokenizer = SimpleTokenizer()
    pairs = list(mem.training().items())
    chain = MarkovChain(tokenizer)
    chain.train_pairs(pairs)
    chain.save(MODEL_PATH)
    mem.close()
    print(f"Model trained and saved to {MODEL_PATH}")

if __name__ == '__main__':
    main()
