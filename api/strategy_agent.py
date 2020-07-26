import shelve
from random import choice

import numpy as np

from api.agent import Agent
from api.game import Game


class GameNode:
    def __init__(self, num_actions: int):
        self.sum_regret = np.zeros(num_actions, dtype=float)
        self.sum_strategy = np.zeros(num_actions, dtype=float)

    def get_strategy(self) -> np.ndarray:
        total = 0
        for regret in self.sum_regret:
            if regret > 0:
                total += regret

        if total > 0.0:
            strategy = np.zeros(len(self.sum_regret), dtype=float)
            for i, value in enumerate(self.sum_regret):
                strategy[i] = max(0.0, value / total)
        else:
            return np.full(len(self.sum_regret), 1.0 / len(self.sum_regret), dtype=float)

        return strategy

    def get_trained_strategy(self) -> np.ndarray:
        total = 0
        for regret in self.sum_strategy:
            if regret > 0:
                total += regret

        if total > 0.0:
            strategy = np.zeros(len(self.sum_strategy), dtype=float)
            for i, value in enumerate(self.sum_strategy):
                strategy[i] = max(0.0, value / total)
        else:
            return np.full(len(self.sum_strategy), 1.0 / len(self.sum_strategy), dtype=float)

        return strategy

    def __str__(self):
        result = ' '
        total = sum(self.sum_strategy)
        for i in range(len(self.sum_strategy)):
            result += '  '
            if total == 0:
                result += str(1.0 / len(self.sum_strategy))
            else:
                result += str(self.sum_strategy[i] / total)
        return result


class StrategyAgent(Agent):
    def __init__(self):
        super().__init__()
        self.game_tree = shelve.open('strategies/basic')
        self.unknown_states = 0

    def get_action(self, game) -> int:
        info_set = self.generate_info_set(game)
        actions = self.generate_actions(game)
        if info_set in self.game_tree:
            action = np.random.choice(actions, p=self.game_tree[info_set].get_trained_strategy())
        else:
            self.unknown_states += 1
            action = choice(actions)
        return self.resolve_action(game, action)

    def reset(self) -> None:
        super().reset()
        self.unknown_states = 0

    def generate_info_set(self, game: Game) -> str:
        pass

    def generate_actions(self, game: Game) -> np.ndarray:
        return game.get_actions()

    def resolve_action(self, game: Game, initial_action: int) -> int:
        return initial_action

    def train(self, game: Game, trials: int):
        for i in range(trials):
            self.__train(game, 1.0, 1.0, i % 2)
            game.reset()

    def __train(self, game: Game, pi: float, pi_prime: float, training_player: int) -> tuple:
        player = game.get_active_player()
        actions = self.generate_actions(game)

        if game.is_finished():
            utility = game.get_utility()
            return utility[player] / pi_prime, 1.0

        info_set = self.generate_info_set(game)
        if info_set in self.game_tree:
            node = self.game_tree[info_set]
        else:
            node = GameNode(len(actions))

        strategy = node.get_strategy()

        epsilon = 0.6
        if player == training_player:
            probability = np.zeros(len(actions), dtype=float)
            for action in range(len(actions)):
                probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
        else:
            probability = np.copy(strategy)

        action_index = np.random.choice(len(probability), p=probability)
        game.preform(self.resolve_action(game, actions[action_index]))
        result = self.__train(game, pi * strategy[action_index], pi_prime * probability[action_index], training_player) if player == training_player else self.__train(game, pi, pi_prime, training_player)
        util = -result[0]
        p_tail = result[1]

        if player == training_player:
            w = util * p_tail
            for action in range(len(actions)):
                regret = w * (1 - strategy[action_index]) if action == action_index else -w * strategy[action_index]
                node.sum_regret[action] += regret
        else:
            for action in range(len(actions)):
                node.sum_strategy[action] += strategy[action] / pi_prime

        self.game_tree[info_set] = node

        if player == training_player:
            return util, p_tail * strategy[action_index]
        else:
            return util, p_tail
