import numpy as np

from game import Game
from my_math import choice_weighted


class GameNode:
    def __init__(self, actions: np.ndarray):
        self.actions = actions
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


class CFRMinimizer:
    def __init__(self, game: Game, info_set_generator, action_generator, action_mapper=None):
        self.game = game
        self.info_set_generator = info_set_generator
        self.action_generator = action_generator
        self.action_mapper = action_mapper
        self.game_tree = {}

    def train(self, trials: int) -> dict:
        for i in range(trials):
            self.__train(1.0, 1.0, i % 2)
            self.game.reset()

    def get_strategy(self) -> dict:
        strategy = {}
        for key in self.game_tree:
            strategy[key] = self.game_tree[key].get_trained_strategy()
        return strategy

    def __train(self, pi: float, pi_prime: float, training_player: int) -> tuple:
        player = self.game.get_active_player()
        actions = self.action_generator(self.game)

        if self.game.is_finished():
            utility = self.game.get_utility()
            return utility[player] / pi_prime, 1.0

        info_set = self.info_set_generator(self.game)
        if info_set in self.game_tree:
            node = self.game_tree[info_set]
        else:
            node = GameNode(actions)
            self.game_tree[info_set] = node

        strategy = node.get_strategy()

        epsilon = 0.6
        if player == training_player:
            probability = np.zeros(len(actions), dtype=float)
            for action in range(len(actions)):
                probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
        else:
            probability = np.copy(strategy)

        chosen_action = choice_weighted(probability)
        if self.action_mapper is not None:
            self.game.preform(self.action_mapper(self.game, actions[chosen_action]))
        else:
            self.game.preform(actions[chosen_action])
        result = self.__train(pi * strategy[chosen_action], pi_prime * probability[chosen_action], training_player) if player == training_player else self.__train(pi, pi_prime, training_player)
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
