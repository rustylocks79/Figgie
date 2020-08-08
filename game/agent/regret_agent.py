from math import floor, ceil

import numpy as np

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.agent.basic_agent import PlusOneAgent
from game.figgie import Figgie, NUM_PLAYERS, Market
from game.suit import Suit


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
    def __init__(self, util_model, game_tree=None):
        super().__init__()
        if game_tree is None:
            game_tree = {}
        self.game_tree = game_tree
        self.unknown_states = 0
        self.util_model = util_model
        self.default_agent = PlusOneAgent(util_model)

    def get_configuration(self, figgie: Figgie):
        player = figgie.active_player
        market = figgie.markets[Suit.CLUBS.value]
        card_util = round(self.util_model.get_card_utility(figgie, player, Suit.CLUBS))
        actual_util = round(self.cheating_model.get_card_utility(figgie, player, Suit.CLUBS))
        self.add_prediction(card_util, actual_util)
        if market.can_buy(player)[0]:
            # if the utility gained by buying the card is greater than the cost of the card.
            if card_util > market.selling_price:
                return None, BuyAction(Suit.CLUBS)
        elif market.can_sell(player)[0]:
            # if the utility lost by selling the card is less than the value received for selling the card.
            if card_util < market.buying_price:
                return None, SellAction(Suit.CLUBS)

        will_bid = (not market.is_buyer() or card_util > market.buying_price + 1) and market.buying_player != player
        will_ask = (not market.is_seller() or card_util < market.selling_price - 1) and market.selling_player != player and \
                    figgie.cards[player][Suit.CLUBS.value] > 0
        will_at = will_bid and will_ask and (not market.is_buyer() or not market.is_seller() or market.buying_price + 1 < card_util < market.selling_price - 1)
        if will_at:
            info_set = 'at util: {}, market: {}, market: {}'.format(card_util, market.buying_price, market.selling_price)
            actions = []
            min_buy = market.buying_price + 1 if market.is_buyer() else 1
            max_sell = market.selling_price - 1 if market.is_seller() else 12
            for i in range(min_buy, min_buy + 8, 1):
                for j in range(max_sell, max(max_sell - 8, i), -1):
                    actions.append(AtAction(Suit.CLUBS, i, j))
        elif will_bid:
            info_set = 'bid util: {}, market: {}'.format(card_util, market.buying_price if market.is_buyer() else 'N')
            actions = []
            min_buy = market.buying_price + 1 if market.buying_price is not None else 1
            for i in range(min_buy, min_buy + 8, 2):
                actions.append(BidAction(Suit.CLUBS, i))
        elif will_ask:
            info_set = 'ask util: {}, market {}'.format(card_util, market.selling_price if market.is_seller() else 'N')
            actions = []
            max_sell = market.selling_price - 1 if market.selling_price is not None else 8
            for i in range(max_sell, max(max_sell - 8, 1), -2):
                actions.append(AskAction(Suit.CLUBS, i))
        else:
            return None, PassAction()
        if len(actions) == 0:
            assert False, 'action list can not be empty info set: {}'.format(info_set)
        return info_set, actions

    def get_action(self, figgie, training_mode: bool = False) -> Action:
        info_set, actions = self.get_configuration(figgie)
        if info_set is None:  # Action chosen by market
            return actions
        elif info_set in self.game_tree:
            return np.random.choice(actions, p=self.game_tree[info_set].get_trained_strategy())
        else:
            self.unknown_states += 1
            return self.default_agent.get_action(figgie)

    def reset(self) -> None:
        super().reset()
        self.unknown_states = 0

    def train(self, game: Figgie, trials: int):
        for i in range(trials):
            self.__train(game, 1.0, 1.0, i % NUM_PLAYERS)
            game.reset()

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
