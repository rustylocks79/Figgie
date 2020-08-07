import shelve
from math import floor, ceil
from random import choice

import numpy as np

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.figgie import Figgie
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
    def __init__(self, index: int, util_model, game_tree=None):
        super().__init__(index)
        if game_tree is None:
            game_tree = {}
        self.game_tree = game_tree
        self.unknown_states = 0
        self.util_model = util_model

    def get_action(self, figgie) -> Action:
        market = figgie.markets[Suit.CLUBS.value]
        buy_exp_util = self.util_model.get_utility_change_from_buy(figgie, self.index, Suit.CLUBS)
        sell_exp_util = self.util_model.get_utility_change_from_sell(figgie, self.index, Suit.CLUBS)
        if market.can_buy(self.index)[0]:
            if buy_exp_util > market.selling_price:
                return BuyAction(self.index, '', Suit.CLUBS)
        elif market.can_sell(self.index)[0]:
            if abs(sell_exp_util) < market.buying_price:
                return SellAction(self.index, '', Suit.CLUBS)

        # Create Info Set and actions
        will_buy = (market.buying_price is None or market.buying_price < buy_exp_util) and market.buying_player != self.index
        will_sell = (market.selling_price is None or market.selling_price > sell_exp_util) and market.selling_player != self.index and \
                    figgie.cards[self.index][Suit.CLUBS.value] > 0
        # if will_buy and will_sell:
        #     info_set = 'at {} {}'.format(round(buy_exp_util), round(sell_exp_util))
        if will_buy:
            info_set = 'bid exp: {}, market: {}'.format(round(buy_exp_util),
                                                        market.buying_price if market.buying_price is not None else 'N')
            if market.buying_price is None:
                actions = [BidAction(self.index, '', Suit.CLUBS, 1),
                           BidAction(self.index, '', Suit.CLUBS, 2),
                           BidAction(self.index, '', Suit.CLUBS, 4),
                           BidAction(self.index, '', Suit.CLUBS, 8)]
            else:
                actions = [BidAction(self.index, '', Suit.CLUBS, market.buying_price + 1),
                           BidAction(self.index, '', Suit.CLUBS, market.buying_price + 2),
                           BidAction(self.index, '', Suit.CLUBS, market.buying_price + 4),
                           BidAction(self.index, '', Suit.CLUBS, market.buying_price + 8)]
        elif will_sell:
            info_set = 'ask exp:{}, market {}'.format(round(sell_exp_util), market.selling_price if market.selling_price is not None else 'N')
            if market.selling_price is None:
                actions = [AskAction(self.index, '', Suit.CLUBS, 1),
                           AskAction(self.index, '', Suit.CLUBS, 2),
                           AskAction(self.index, '', Suit.CLUBS, 4),
                           AskAction(self.index, '', Suit.CLUBS, 8)]
            else:
                actions = []
                for i in [1, 2, 4, 8]:
                    if market.selling_price - i > 0:
                        actions.append(AskAction(self.index, '', Suit.CLUBS, market.selling_price - i))
        else:
            return PassAction(self.index, '')

        if info_set in self.game_tree:
            return np.random.choice(actions, p=self.game_tree[info_set].get_trained_strategy())
        else:
            buying_price = max(floor(buy_exp_util) - 1, 1)
            selling_price = max(abs(ceil(sell_exp_util)) + 1, 1)

            will_buy = market.can_bid(self.index, buying_price)[0]
            will_sell = market.can_ask(self.index, selling_price)[0]

            if will_buy and will_sell:
                if buying_price >= selling_price:  # TODO: this is a temp fix
                    return BidAction(self.index, '', Suit.CLUBS, buying_price)
                return AtAction(self.index, '', Suit.CLUBS, buying_price, selling_price)
            elif will_buy:
                return BidAction(self.index, '', Suit.CLUBS, buying_price)
            elif will_sell:
                return AskAction(self.index, '', Suit.CLUBS, selling_price)
            else:
                return PassAction(self.index, '')

    def reset(self) -> None:
        super().reset()
        self.unknown_states = 0

    def train(self, game: Figgie, trials: int):
        for i in range(trials):
            self.__train(game, 1.0, 1.0, i % 2)
            game.reset()

    def __train(self, figgie: Figgie, pi: float, pi_prime: float, training_player: int) -> tuple:
        player = figgie.get_active_player()
        if figgie.is_finished():
            utility = figgie.get_utility()
            return utility[player] / pi_prime, 1.0

        market = figgie.markets[Suit.CLUBS.value]
        buy_exp_util = self.util_model.get_utility_change_from_buy(figgie, player, Suit.CLUBS)
        sell_exp_util = self.util_model.get_utility_change_from_sell(figgie, player, Suit.CLUBS)
        if market.can_buy(player)[0]:
            if buy_exp_util > market.selling_price:
                figgie.preform(BuyAction(player, '', Suit.CLUBS))
                return self.__train(figgie, pi, pi_prime, training_player)
        elif market.can_sell(player)[0]:
            if abs(sell_exp_util) < market.buying_price:
                figgie.preform(SellAction(player, '', Suit.CLUBS))
                return self.__train(figgie, pi, pi_prime, training_player)

        # Create Info Set and actions
        will_buy = (market.buying_price is None or market.buying_price < buy_exp_util) and market.buying_player != player
        will_sell = (market.selling_price is None or market.selling_price > sell_exp_util) and market.selling_player != player and \
                    figgie.cards[player][Suit.CLUBS.value] > 0
        # if will_buy and will_sell:
        #     info_set = 'at {} {}'.format(round(buy_exp_util), round(sell_exp_util))
        if will_buy:
            info_set = 'bid exp: {}, market: {}'.format(round(buy_exp_util), market.buying_price if market.buying_price is not None else 'N')
            if market.buying_price is None:
                actions = [BidAction(player, '', Suit.CLUBS, 1),
                           BidAction(player, '', Suit.CLUBS, 2),
                           BidAction(player, '', Suit.CLUBS, 4),
                           BidAction(player, '', Suit.CLUBS, 8)]
            else:
                actions = [BidAction(player, '', Suit.CLUBS, market.buying_price + 1),
                           BidAction(player, '', Suit.CLUBS, market.buying_price + 2),
                           BidAction(player, '', Suit.CLUBS, market.buying_price + 4),
                           BidAction(player, '', Suit.CLUBS, market.buying_price + 8)]
        elif will_sell:
            info_set = 'ask exp:{}, market {}'.format(round(sell_exp_util), market.selling_price if market.selling_price is not None else 'N')
            if market.selling_price is None:
                actions = [AskAction(player, '', Suit.CLUBS, 1),
                           AskAction(player, '', Suit.CLUBS, 2),
                           AskAction(player, '', Suit.CLUBS, 4),
                           AskAction(player, '', Suit.CLUBS, 8)]
            else:
                actions = []
                for i in [1, 2, 4, 8]:
                    if market.selling_price - i > 0:
                        actions.append(AskAction(player, '', Suit.CLUBS, market.selling_price - i))
        else:
            figgie.preform(PassAction(player, ''))
            return self.__train(figgie, pi, pi_prime, training_player)

        if info_set in self.game_tree:
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
