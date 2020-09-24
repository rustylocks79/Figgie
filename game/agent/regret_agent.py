import numpy as np

from game.action.action import Action
from game.action.pass_action import PassAction
from game.agent.agent import Agent
from game.agent.modular_agent import ModularAgent
from game.figgie import Figgie, NUM_PLAYERS
from game.suit import Suit


class InfoSetGenerator:
    def __init__(self, name):
        self.name = name

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        pass

    def generate_actions(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit) -> list:
        market = figgie.markets[target_suit.value]
        if target_operation == 'bid':
            return self.generate_bid_actions(card_util, market.buying_price, target_suit)
        elif target_operation == 'ask':
            return self.generate_ask_actions(card_util, market.selling_price, target_suit)
        elif target_operation == 'at':
            return self.generate_at_actions(card_util, market.buying_price, market.selling_price, target_suit)
        else:
            raise ValueError('Best action can not be: {}'.format(target_suit))

    def generate_bid_actions(self, card_util: float, buying_price: int, target_suit: Suit) -> list:
        pass

    def generate_ask_actions(self, card_util: float, selling_price: int, target_suit: Suit) -> list:
        pass

    def generate_at_actions(self, card_util: float, buying_price: int, selling_price: int, target_suit: Suit) -> list:
        pass


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
            return strategy
        else:
            return np.full(len(self.sum_regret), 1.0 / len(self.sum_regret), dtype=float)

    def get_trained_strategy(self) -> np.ndarray:
        total = 0
        for regret in self.sum_strategy:
            if regret > 0:
                total += regret

        if total > 0.0:
            strategy = np.zeros(len(self.sum_strategy), dtype=float)
            for i, value in enumerate(self.sum_strategy):
                strategy[i] = max(0.0, value / total)
            return strategy
        else:
            return np.full(len(self.sum_strategy), 1.0 / len(self.sum_strategy), dtype=float)

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


class RegretAgent(Agent):
    def __init__(self, util_model, info_set_generator: InfoSetGenerator, default_agent: Agent, game_tree: dict = None):
        super().__init__()
        if game_tree is None:
            game_tree = {}
        self.game_tree = game_tree
        self.unknown_states = 0
        self.util_model = util_model
        self.info_set_generator = info_set_generator
        self.default_agent = default_agent

    def reset(self) -> None:
        super().reset()
        self.util_model.reset()

    def get_configuration(self, figgie: Figgie):
        utils = ModularAgent.calc_card_utils(self, figgie)
        best_transaction = ModularAgent.get_best_transaction(figgie, utils)
        if best_transaction is not None:
            return None, best_transaction

        best_action, best_adv, best_suit = ModularAgent.get_best_market_adv(figgie, utils)
        if best_action is not None:
            info_set = self.info_set_generator.generate_info_set(figgie, utils[best_suit.value], best_action, best_suit)
            actions = self.info_set_generator.generate_actions(figgie, utils[best_suit.value], best_action, best_suit)
            assert len(actions) != 0, 'Length of actions == 0'
            return info_set, actions

        return None, PassAction()

    def get_action(self, figgie, training_mode: bool = False) -> Action:
        info_set, actions = self.get_configuration(figgie)
        if info_set is None:  # Action chosen by market
            return actions
        elif info_set in self.game_tree:
            percents = self.game_tree[info_set].get_trained_strategy()
            action = np.random.choice(actions, p=percents)
            if figgie.can_preform(action):
                return action
            else:
                return PassAction()
        else:
            self.unknown_states += 1
            return self.default_agent.get_action(figgie)

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)

    def train(self, game: Figgie, trials: int):
        for i in range(trials):
            self.__train(game, 1.0, 1.0, i % NUM_PLAYERS)
            game.reset()
            self.reset()

    def __train(self, figgie: Figgie, pi: float, pi_prime: float, training_player: int) -> tuple:
        player = figgie.active_player
        if figgie.is_finished():
            utility = figgie.get_utility()
            return utility[player] / pi_prime, 1.0

        info_set, actions = self.get_configuration(figgie)
        if info_set is None:
            figgie.preform(actions)
            return self.__train(figgie, pi, pi_prime, training_player)
        elif info_set in self.game_tree:
            node = self.game_tree[info_set]
        else:
            node = GameNode(len(actions))
            self.game_tree[info_set] = node

        strategy = node.get_strategy()

        epsilon = 0.6
        if player == training_player:
            probability = np.zeros(len(actions), dtype=float)
            for action in range(len(actions)):
                probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
        else:
            probability = np.copy(strategy)

        action_index = np.random.choice(len(probability), p=probability)
        if figgie.can_preform(actions[action_index]):
            figgie.preform(actions[action_index])
        else:
            figgie.preform(PassAction())
            return self.__train(figgie, pi, pi_prime, training_player)
        self.on_action(figgie, player, actions[action_index])
        result = self.__train(figgie, pi * strategy[action_index], pi_prime * probability[action_index], training_player) if player == training_player else self.__train(figgie, pi, pi_prime, training_player)
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

        if player == training_player:
            return util, p_tail * strategy[action_index]
        else:
            return util, p_tail
