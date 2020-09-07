import numpy as np

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.agent.modular_agent import ModularAgent
from game.figgie import Figgie, NUM_PLAYERS
from game.suit import Suit


class InfoSetGenerator:
    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
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
        self.transactions = np.full(4, 0, dtype=int)

    def get_configuration(self, figgie: Figgie):
        player = figgie.active_player
        hand = figgie.cards[player]
        utils = ModularAgent.calc_card_utils(self, figgie)
        best_action, best_adv, best_suit = ModularAgent.get_best_transaction(figgie, utils)
        if best_action is not None:
            player = figgie.active_player
            market = figgie.markets[best_suit.value]
            if best_action == 'buy':
                assert market.can_buy(player)[0], market.can_buy(player)[1]
                return None, BuyAction(best_suit, notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            elif best_action == 'sell':
                assert market.can_sell(player)[0], market.can_sell(player)[1]
                return None, SellAction(best_suit, notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

        best_action, best_adv, best_suit = ModularAgent.get_best_market_adv(figgie, utils)
        if best_action is not None:
            market = figgie.markets[best_suit.value]
            info_set = self.info_set_generator.generate_info_set(best_action, best_suit, figgie, self, utils[best_suit.value])
            if best_action == 'bid':
                actions = []
                min_buy = market.buying_price + 1 if market.buying_price is not None else 1
                for i in range(min_buy, min_buy + 8):
                    actions.append(BidAction(best_suit, i))
                return info_set, actions
            elif best_action == 'ask':
                actions = []
                max_sell = market.selling_price if market.selling_price is not None else int(utils[best_suit.value] * 2)
                for i in range(max(max_sell - 8, 1), max_sell):
                    actions.append(AskAction(best_suit, i))
                return info_set, actions
            elif best_action == 'at':
                actions = []
                min_buy = market.buying_price + 1 if market.is_buyer() else 1
                max_sell = market.selling_price if market.is_seller() else int(utils[best_suit.value]) + 8
                for i in range(min_buy, min_buy + 8):
                    for j in range(max(max_sell - 8, i + 1), max_sell):
                        actions.append(AtAction(best_suit, i, j))
                return info_set, actions
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

        return None, PassAction()

    def get_action(self, figgie, training_mode: bool = False) -> Action:
        info_set, actions = self.get_configuration(figgie)
        if info_set is None:  # Action chosen by market
            return actions
        elif info_set in self.game_tree:
            return np.random.choice(actions, p=self.game_tree[info_set].get_trained_strategy())
        else:
            self.unknown_states += 1
            return self.default_agent.get_action(figgie)

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)
        if not isinstance(action, PassAction):
            self.transactions[action.suit.value] += 1

    def reset(self) -> None:
        super().reset()
        self.unknown_states = 0
        self.transactions = np.full(4, 0, dtype=int)

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
        figgie.preform(actions[action_index])
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


class BasicInfoSetGenerator(InfoSetGenerator):
    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        market = figgie.markets[suit.value]
        hand = figgie.cards[figgie.active_player]
        if action == 'bid':
            return 'bid,{},{},{}'.format(util, market.buying_price if market.is_buyer() else 'N',
                                         hand[suit.value])
        elif action == 'ask':
            return 'ask,{},{},{}'.format(util, market.selling_price if market.is_seller() else 'N',
                                         hand[suit.value])
        elif action == 'at':
            return 'at,{},{},{},{}'.format(util, market.buying_price if market.is_buyer() else 'N',
                                           market.selling_price if market.is_seller() else 'N',
                                           hand[suit.value])
        else:
            raise ValueError("Invalid action: {}".format(action))


class AdvInfoSetGenerator(InfoSetGenerator):
    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        market = figgie.markets[suit.value]
        hand = figgie.cards[figgie.active_player]
        if action == 'bid':
            return 'bid,{},{},{},{}'.format(util, market.buying_price if market.is_buyer() else 'N',
                                         hand[suit.value], agent.transactions[suit.value])
        elif action == 'ask':
            return 'ask,{},{},{},{}'.format(util, market.selling_price if market.is_seller() else 'N',
                                         hand[suit.value], agent.transactions[suit.value])
        elif action == 'at':
            return 'at,{},{},{},{},{}'.format(util, market.buying_price if market.is_buyer() else 'N',
                                           market.selling_price if market.is_seller() else 'N',
                                           hand[suit.value], agent.transactions[suit.value])
        else:
            raise ValueError("Invalid action: {}".format(action))
