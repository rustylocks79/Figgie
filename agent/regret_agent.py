import numpy as np

from agent.agent import Agent
from agent.choosers.simple_chooser import SimpleChooser
from agent.modular_agent import ModularAgent
from figgie import Figgie, NUM_PLAYERS, Suit, Action


class InfoSetGenerator:
    def __init__(self, name):
        self.name = name

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        pass

    def generate_actions(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit) -> np.ndarray:
        market = figgie.markets[target_suit.value]
        if target_operation == 'bid':
            return self.generate_bid_actions(card_util, market.buying_price, target_suit)
        elif target_operation == 'ask':
            return self.generate_ask_actions(card_util, market.selling_price, target_suit)
        elif target_operation == 'at':
            return self.generate_at_actions(card_util, market.buying_price, market.selling_price, target_suit)
        else:
            raise ValueError('Best action can not be: {}'.format(target_suit))

    def generate_bid_actions(self, card_util: float, buying_price: int, target_suit: Suit) -> np.ndarray:
        pass

    def generate_ask_actions(self, card_util: float, selling_price: int, target_suit: Suit) -> np.ndarray:
        pass

    def generate_at_actions(self, card_util: float, buying_price: int, selling_price: int, target_suit: Suit) -> np.ndarray:
        pass


class GameNode:
    def __init__(self, num_actions: int):
        self.sum_regret = np.zeros(num_actions, dtype=float)
        self.sum_strategy = np.zeros(num_actions, dtype=float)
        self.observations = 0

    def get_strategy(self) -> np.ndarray:
        total = np.sum(self.sum_regret, where=self.sum_regret > 0)
        if total > 0.0:
            strategy = np.true_divide(self.sum_regret, total)
            strategy[strategy < 0] = 0
            return strategy
        else:
            return np.full(len(self.sum_regret), 1.0 / len(self.sum_regret), dtype=float)

    def get_trained_strategy(self) -> np.ndarray:
        total = np.sum(self.sum_strategy, where=self.sum_strategy > 0)
        if total > 0.0:
            strategy = np.true_divide(self.sum_strategy, total)
            strategy[strategy < 0] = 0
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
    def __init__(self, util_model, chooser: SimpleChooser, info_set_generator: InfoSetGenerator, default_agent: Agent, game_tree: dict = None, collector=False):
        super().__init__('Regret Agent', collector=collector)
        if game_tree is None:
            game_tree = {}
        self.game_tree = game_tree
        self.unknown_states = 0
        self.util_model = util_model
        self.chooser = chooser
        self.info_set_generator = info_set_generator
        self.default_agent = default_agent

    def reset(self) -> None:
        super().reset()
        self.util_model.reset()

    @staticmethod
    def create_action(operation, suit, price) -> Action:
        if operation == 'ask':
            return Action.ask(suit, price)
        elif operation == 'bid':
            return Action.bid(suit, price)
        elif operation == 'at':
            return Action.at(suit, price[0], price[1])
        else:
            raise ValueError('Invalid Operation: {}'.format(operation))

    def get_action(self, figgie, training_mode: bool = False) -> Action:
        player = figgie.active_player
        utils = self.util_model.get_card_utility(figgie, player)
        self.collect(figgie)
        best_transaction = ModularAgent.get_best_transaction(figgie, utils)
        if best_transaction is not None:
            return best_transaction

        best_action, best_adv, best_suit = self.chooser.get_best_market_adv(figgie, utils)
        if best_action is not None:
            info_set = self.info_set_generator.generate_info_set(figgie, round(utils[best_suit.value]), best_action,
                                                                 best_suit)
            actions = self.info_set_generator.generate_actions(figgie, round(utils[best_suit.value]), best_action,
                                                               best_suit)
            assert len(actions) != 0, 'Length of actions == 0'
            if info_set in self.game_tree:
                percents = self.game_tree[info_set].get_trained_strategy()
                price = np.random.choice(actions, p=percents)
                action = self.create_action(best_action, best_suit, price)
                if figgie.can_preform(action):
                    return action
                else:
                    return Action.passing()
            else:
                self.unknown_states += 1
                return self.default_agent.get_action(figgie)
        return Action.passing()

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

        player = figgie.active_player
        utils = self.util_model.get_card_utility(figgie, player)
        best_transaction = ModularAgent.get_best_transaction(figgie, utils)
        if best_transaction is not None:
            figgie.preform(best_transaction)
            return self.__train(figgie, pi, pi_prime, training_player)

        best_action, best_adv, best_suit = self.chooser.get_best_market_adv(figgie, utils)
        if best_action is None:
            figgie.preform(Action.passing())
            return self.__train(figgie, pi, pi_prime, training_player)
        else:
            info_set = self.info_set_generator.generate_info_set(figgie, round(utils[best_suit.value]), best_action,
                                                                 best_suit)
            actions = self.info_set_generator.generate_actions(figgie, round(utils[best_suit.value]), best_action,
                                                               best_suit)
            assert len(actions) != 0, 'Length of actions == 0'
            if info_set in self.game_tree:
                node = self.game_tree[info_set]
            else:
                node = GameNode(len(actions))
                self.game_tree[info_set] = node

        strategy = node.get_strategy()

        epsilon = 0.6
        if player == training_player:
            probability = epsilon / len(actions) + ((1.0 - epsilon) * strategy)
        else:
            probability = np.copy(strategy)

        action_index = np.random.choice(len(actions), p=probability)
        price = actions[action_index]
        action = self.create_action(best_action, best_suit, price)
        if figgie.can_preform(action):
            figgie.preform(action)
        else:
            figgie.preform(Action.passing())
            return self.__train(figgie, pi, pi_prime, training_player)
        self.on_action(figgie, player, action)
        result = self.__train(figgie, pi * strategy[action_index], pi_prime * probability[action_index], training_player) if player == training_player else self.__train(figgie, pi, pi_prime, training_player)
        util = -result[0]
        p_tail = result[1]

        if player == training_player:
            w = util * p_tail
            regret = w * (1 - strategy)
            regret[action_index] = -w * strategy[action_index]
            node.sum_regret += regret
        else:
            node.sum_strategy += strategy / pi_prime

        node.observations += 1

        if player == training_player:
            return util, p_tail * strategy[action_index]
        else:
            return util, p_tail
