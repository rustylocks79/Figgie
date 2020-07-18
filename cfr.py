from random import choice

import numpy as np

from game import Game, Agent
from my_math import choice_weighted


class InfoSetGenerator:
    def __init__(self, name):
        self.name = name

    def generate(self, game) -> str:
        pass


class StrategyAgent(Agent):
    def __init__(self, strategy, info_set_generator: InfoSetGenerator):
        super().__init__()
        self.strategy = strategy
        self.info_set_generator = info_set_generator
        self.unknown_states = 0

    def get_action(self, game) -> str:
        info_set = self.info_set_generator.generate(game)
        actions = game.get_actions()
        if info_set in self.strategy:
            return actions[choice_weighted(self.strategy[info_set])]
        else:
            self.unknown_states += 1
            return choice(actions)


class GameNode:
    def __init__(self, actions: list):
        self.num_actions = len(actions)
        self.sum_regret = np.zeros(len(actions), dtype=float)
        self.sum_strategy = np.zeros(len(actions), dtype=float)

    def get_strategy(self) -> np.ndarray:
        total = 0
        for regret in self.sum_regret:
            if regret > 0:
                total += regret

        if total > 0.0:
            strategy = np.zeros(self.num_actions, dtype=float)
            for i in range(self.num_actions):
                strategy[i] = max(0.0, self.sum_regret[i] / total)
        else:
            return np.full(self.num_actions, 1.0 / self.num_actions, dtype=float)

        return strategy

    def get_trained_strategy(self) -> np.ndarray:
        total = 0
        for regret in self.sum_strategy:
            if regret > 0:
                total += regret

        if total > 0.0:
            strategy = np.zeros(self.num_actions, dtype=float)
            for i in range(self.num_actions):
                strategy[i] = max(0.0, self.sum_strategy[i] / total)
        else:
            return np.full(self.num_actions, 1.0 / self.num_actions, dtype=float)

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


def train(game: Game, info_set_generator: InfoSetGenerator, trials: int) -> dict:
    game_tree = {}
    for i in range(trials):
        __train(game, info_set_generator, game_tree, 1.0, 1.0, i % 2)
        game.reset()

    strategy = {}
    for key in game_tree:
        strategy[key] = game_tree[key].get_trained_strategy()
    return strategy


def __train(game: Game, info_set_generator: InfoSetGenerator, game_tree: map, pi: float, pi_prime: float, training_player: int) -> tuple:
    player = game.get_active_player()
    actions = game.get_actions()

    if game.is_finished():
        return game.get_utility(player) / pi_prime, 1.0

    info_set = info_set_generator.generate(game)
    if info_set in game_tree:
        node = game_tree[info_set]
    else:
        node = GameNode(actions)
        game_tree[info_set] = node

    strategy = node.get_strategy()

    probability = np.zeros(len(actions), dtype=float)
    epsilon = 0.6
    for action in range(len(actions)):
        if player == training_player:
            probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
        else:
            probability[action] = strategy[action]

    chosen_action = choice_weighted(probability)
    game.preform(actions[chosen_action])
    result = __train(game, info_set_generator, game_tree, pi * strategy[chosen_action], pi_prime * probability[chosen_action],
                     training_player) if player == training_player else __train(game, info_set_generator, game_tree, pi,
                                                                                pi_prime, training_player)

    util = -result[0]
    p_tail = result[1]

    if player == training_player:
        W = util * p_tail
        for action in range(len(actions)):
            regret = W * (1 - strategy[chosen_action]) if action == chosen_action else -W * strategy[chosen_action]
            node.sum_regret[action] += regret
    else:
        for action in range(len(actions)):
            node.sum_strategy[action] += strategy[action] / pi_prime

    if player == training_player:
        return util, p_tail * strategy[chosen_action]
    else:
        return util, p_tail
