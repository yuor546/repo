import pickle
import random
import numpy as np

MODEL_PATH = 'q_table.pkl'
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1


def check_winner(board):
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
    for a, b, c in wins:
        if board[a] == board[b] == board[c] != ' ':
            return board[a]
    return None


def available_moves(board):
    return [i for i, c in enumerate(board) if c == ' ']


def board_key(board):
    return ''.join(board)


def choose_move(board, q_table):
    moves = available_moves(board)
    if random.random() < EPSILON:
        return random.choice(moves)
    key = board_key(board)
    qvals = q_table.get(key, np.zeros(9))
    best = max(moves, key=lambda m: qvals[m])
    return best


def main(episodes: int = 5000):
    q_table = {}
    for _ in range(episodes):
        board = [' '] * 9
        state_key = board_key(board)
        move = choose_move(board, q_table)
        prev_key, prev_move = state_key, move
        mark = 'X'
        while True:
            board[move] = mark
            winner = check_winner(board)
            if winner or ' ' not in board:
                reward = 1 if winner == 'X' else 0 if winner is None else -1
                q_table.setdefault(prev_key, np.zeros(9))
                q_table[prev_key][prev_move] += ALPHA * (reward - q_table[prev_key][prev_move])
                break
            # opponent random move
            o_move = random.choice(available_moves(board))
            board[o_move] = 'O'
            winner = check_winner(board)
            if winner or ' ' not in board:
                reward = 1 if winner == 'X' else 0 if winner is None else -1
                q_table.setdefault(prev_key, np.zeros(9))
                q_table[prev_key][prev_move] += ALPHA * (reward - q_table[prev_key][prev_move])
                break
            next_key = board_key(board)
            next_move = choose_move(board, q_table)
            q_table.setdefault(prev_key, np.zeros(9))
            q_table.setdefault(next_key, np.zeros(9))
            q_table[prev_key][prev_move] += ALPHA * (GAMMA * np.max(q_table[next_key]) - q_table[prev_key][prev_move])
            prev_key, prev_move = next_key, next_move
            move = next_move
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(q_table, f)
    print('Q-table saved to', MODEL_PATH)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', type=int, default=5000)
    args = parser.parse_args()
    main(args.episodes)
