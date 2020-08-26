import numpy as np

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.figgie import Figgie, Suit
from game.model.utility_model import UtilityModel
from game.suit import SUITS


class BasicAgent(Agent):
    def __init__(self, model: UtilityModel):
        super().__init__()
        self.util_model = model

    def get_action(self, figgie: Figgie) -> Action:
        player = figgie.active_player
        best_action = None
        best_adv = 0
        best_suit = None
        utils = np.full(4, 0, dtype=float)
        for suit in SUITS:
            market = figgie.markets[suit.value]
            card_util = round(self.util_model.get_card_utility(figgie, player, suit))
            actual_util = round(self.cheating_model.get_card_utility(figgie, player, suit))
            self.add_prediction(card_util, actual_util)
            utils[suit.value] = card_util

            if market.can_buy(player)[0]:
                buy_adv = utils[suit.value] - market.selling_price
                if buy_adv > best_adv:
                    best_action = 'buy'
                    best_adv = buy_adv
                    best_suit = suit

            if market.can_sell(player)[0]:
                sell_adv = market.buying_price - utils[suit.value]
                if sell_adv > best_adv:
                    best_action = 'sell'
                    best_adv = sell_adv
                    best_suit = suit

        if best_action is not None:
            if best_action == 'buy':
                return BuyAction(best_suit, notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            elif best_action == 'sell':
                return SellAction(best_suit, notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

        best_action = None
        best_adv = 0
        best_suit = None
        best_price = 0

        for suit in SUITS:
            market = figgie.markets[suit.value]
            buying_price = int(self.get_buying_price(figgie, utils[suit.value]))
            selling_price = int(self.get_selling_price(figgie, utils[suit.value]))
            buy_adv = utils[suit.value] - buying_price
            sell_adv = selling_price - utils[suit.value]

            if market.can_bid(player, buying_price)[0]:
                if buy_adv > best_adv:
                    best_action = 'bid'
                    best_adv = buy_adv
                    best_suit = suit
                    best_price = buying_price

            if market.can_ask(player, selling_price)[0]:
                if sell_adv > best_adv:
                    best_action = 'ask'
                    best_adv = sell_adv
                    best_suit = suit
                    best_price = selling_price

            if market.can_at(player, buying_price, selling_price)[0]:
                at_adv = buy_adv + sell_adv
                if at_adv > best_adv:
                    best_action = 'at'
                    best_adv = at_adv
                    best_suit = suit
                    best_price = (buying_price, selling_price)

        if best_action is not None:
            if best_action == 'bid':
                return BidAction(best_suit, best_price)
            elif best_action == 'ask':
                return AskAction(best_suit, best_price)
            elif best_action == 'at':
                return AtAction(best_suit, best_price[0], best_price[1])

        return PassAction()

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)

    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        pass

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        pass


class PlusOneAgent(BasicAgent):
    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        return max(card_util - 1, 1)

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        return max(card_util + 1, 1)


class MinusOneAgent(BasicAgent):
    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        market = figgie.markets[Suit.CLUBS.value]
        if market.is_buyer():
            return market.buying_price + 1
        else:
            return max(card_util - 1, 1)

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        market = figgie.markets[Suit.CLUBS.value]
        if market.is_seller():
            return market.selling_price - 1
        else:
            return max(card_util + 1, 1)
