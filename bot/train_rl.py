import random
import pickle
import argparse
from collections import defaultdict
import numpy as np
from .games import TicTacToeGame

Q_PATH = 'tictactoe_q.pkl'
EPISODES = 1000
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1
EPS_DECAY = 0.0


def get_state(board: list[str]) -> str:
    return ''.join(board)


def available_actions(board: list[str]):
    return [i for i, c in enumerate(board) if c == ' ']


def choose_action(q, state, actions, epsilon):
    if random.random() < epsilon or state not in q:
        return random.choice(actions)
    q_values = q[state]
    best = max(actions, key=lambda a: q_values[a])
    return best


def train(episodes: int = EPISODES, alpha: float = ALPHA, gamma: float = GAMMA,
          epsilon: float = EPSILON, eps_decay: float = EPS_DECAY,
          q_path: str = Q_PATH):
    q = defaultdict(lambda: np.zeros(9))
    for _ in range(episodes):
        game = TicTacToeGame(0, 1)
        state = get_state(game.state.board)
        done = False
        while not done:
            actions = available_actions(game.state.board)
            action = choose_action(q, state, actions, epsilon)
            msg, end = game.make_move(0, action)
            next_state = get_state(game.state.board)
            reward = 0.0
            if end == 'END':
                reward = 1.0 if 'wins' in msg else 0.5
                q[state][action] += alpha * (reward - q[state][action])
                break
            opp_actions = available_actions(game.state.board)
            if not opp_actions:
                break
            opp_action = random.choice(opp_actions)
            game.make_move(1, opp_action)
            next_state = get_state(game.state.board)
            if game.check_winner():
                reward = -1.0
                done = True
            q[state][action] += alpha * (reward + gamma * np.max(q[next_state]) - q[state][action])
            state = next_state
        if eps_decay:
            epsilon = max(0.01, epsilon * (1.0 - eps_decay))
    with open(q_path, 'wb') as f:
        pickle.dump(dict(q), f)
    print('Q-table saved to', q_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a Tic-Tac-Toe Q-learning agent')
    parser.add_argument('--episodes', type=int, default=EPISODES,
                        help='number of training episodes')
    parser.add_argument('--alpha', type=float, default=ALPHA,
                        help='learning rate')
    parser.add_argument('--gamma', type=float, default=GAMMA,
                        help='discount factor')
    parser.add_argument('--epsilon', type=float, default=EPSILON,
                        help='exploration rate')
    parser.add_argument('--eps-decay', type=float, default=EPS_DECAY,
                        help='epsilon decay per episode')
    parser.add_argument('--q-path', type=str, default=Q_PATH,
                        help='output path for Q-table')
    args = parser.parse_args()
    train(episodes=args.episodes, alpha=args.alpha, gamma=args.gamma,
          epsilon=args.epsilon, eps_decay=args.eps_decay, q_path=args.q_path)
