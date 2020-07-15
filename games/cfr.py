import time

import numpy as np

from games.game import Game
from games.my_math import choice_weighted


class GameNode:
    def __init__(self, actions: list):
        self.num_actions = len(actions)
        self.sum_regret = np.zeros(len(actions), dtype=float)
        self.sum_strategy = np.zeros(len(actions), dtype=float)

    def get_strategy(self) -> np.ndarray:
        strategy = np.zeros(self.num_actions, dtype=float)
        sum = 0
        for regret in self.sum_regret:
            if regret > 0:
                sum += regret

        for i in range(self.num_actions):
            if sum > 0.0:
                strategy[i] = max(0.0, self.sum_regret[i] / sum)
            else:
                strategy[i] = 1.0 / self.num_actions

        return strategy

    def get_trained_strategy(self) -> np.ndarray:
        total = sum(self.sum_strategy)
        strategy = np.zeros(self.num_actions, dtype=float)
        for i in range(self.num_actions):
            if total == 0:
                strategy[i] = 1.0 / self.num_actions
            else:
                strategy[i] += self.sum_strategy[i] / total
        return strategy

    def __str__(self):
        result = ' '
        total = sum(self.sum_strategy)
        for i in range(self.num_actions):
            result += '  '
            if total == 0:
                result += str(1.0 / self.num_actions)
            else:
                result += str(self.sum_strategy[i] / total)
        return result


def train(game: Game, trials: int):
    print('Creating Game Tree: ')
    start_time = time.process_time()
    game_tree = {}
    for i in range(trials):
        __train(game, game_tree, 1.0, 1.0, i % 2)
        game.reset()
    total_time = time.process_time() - start_time
    print('Created Game Tree in {} \n'.format(total_time))

    print('Extracting Strategy: ')
    start_time = time.process_time()
    strategy = {}
    for key in game_tree:
        strategy[key] = game_tree[key].get_trained_strategy()
    total_time = time.process_time() - start_time
    print('Extracted Strategy in {} \n'.format(total_time))
    return strategy, game_tree


def __train(game: Game, game_tree: map, pi: float, pi_prime: float, training_player: int) -> tuple:
    player = game.get_active_player()
    actions = game.get_actions()

    if game.is_finished():
        return game.get_utility(player) / pi_prime, 1.0

    info_set = game.get_info_set()
    if info_set in game_tree:
        node = game_tree[info_set]
    else:
        node = GameNode(actions)
        game_tree[info_set] = node

    strategy = node.get_strategy()

    probability = [0] * len(actions)
    epsilon = 0.6
    for action in range(len(actions)):
        if player == training_player:
            probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
        else:
            probability[action] = strategy[action]

    choice = choice_weighted(probability)
    game.preform(actions[choice])
    result = __train(game, game_tree, pi * strategy[choice], pi_prime * probability[choice],
                     training_player) if player == training_player else __train(game, game_tree, pi, pi_prime,
                                                                                training_player)

    util = -result[0]
    p_tail = result[1]

    if player == training_player:
        W = util * p_tail
        for action in range(len(actions)):
            regret = W * (1 - strategy[choice]) if action == choice else -W * strategy[choice]
            node.sum_regret[action] += regret
    else:
        for action in range(len(actions)):
            node.sum_strategy[action] += strategy[action] / pi_prime

    if player == training_player:
        return util, p_tail * strategy[choice]
    else:
        return util, p_tail
