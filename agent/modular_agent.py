from random import randint

import numpy as np

from agent.agent import Agent
from agent.models.utility_model import UtilityModel
from figgie import Figgie, Suit, Action, SUITS


class BuyPricer:
    def get_buying_price(self, figgie: Figgie, suit: Suit, card_util: int) -> int:
        """
        precondition: card_util > (market.buying_price + 1)
        :param figgie:
        :param suit:
        :param card_util:
        """
        pass


class SellPricer:
    def get_selling_price(self, figgie: Figgie, suit: Suit, card_util: int) -> int:
        """
        precondition (market.selling_price - 1) > card_util
        :param figgie:
        :param suit:
        :param card_util:
        """
        pass


class ModularAgent(Agent):
    def __init__(self, model: UtilityModel, buy_pricer: BuyPricer, sell_pricer: SellPricer):
        super().__init__('Modular Agent')
        self.util_model = model
        self.buy_pricer = buy_pricer
        self.sell_pricer = sell_pricer

    def reset(self) -> None:
        super().reset()
        self.util_model.reset()

    @staticmethod
    def calc_card_utils(agent: Agent, figgie: Figgie) -> np.ndarray:
        player = figgie.active_player
        utils = agent.util_model.get_card_utility(figgie, player)
        actual_utils = agent.cheating_model.get_card_utility(figgie, player)
        for suit in SUITS:
            agent.add_prediction(utils[suit.value], actual_utils[suit.value])
        return utils

    @staticmethod
    def get_best_transaction(figgie: Figgie, utils: np.ndarray):
        player = figgie.active_player
        best_action = None
        best_adv = 0
        best_suit = None
        for suit in SUITS:
            market = figgie.markets[suit.value]
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

        if best_action is None:
            return None
        else:
            player = figgie.active_player
            market = figgie.markets[best_suit.value]
            if best_action == 'buy':
                assert market.can_buy(player)[0], market.can_buy(player)[1]
                return Action.buy(best_suit,
                                 notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            elif best_action == 'sell':
                assert market.can_sell(player)[0], market.can_sell(player)[1]
                return Action.sell(best_suit,
                                  notes='with exp util: {}, adv: {}'.format(utils[best_suit.value], best_adv))
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

    @staticmethod
    def get_best_market_adv(figgie: Figgie, utils: np.ndarray) -> tuple:
        player = figgie.active_player
        best_action = None
        best_adv = 0
        best_suit = None
        for suit in SUITS:
            market = figgie.markets[suit.value]
            if market.has_buyer():
                if figgie.chips[player] > market.buying_price:
                    max_useful_price = min(utils[suit.value], figgie.chips[player])
                    buy_adv = max_useful_price - (market.buying_price + 1) if (market.buying_price + 1) < max_useful_price else None
                else:
                    buy_adv = None
            else:
                buy_adv = utils[suit.value]

            if figgie.cards[player][suit.value] >= 1:
                if market.has_seller():
                    sell_adv = (market.selling_price - 1) - utils[suit.value] if (market.selling_price - 1) > utils[suit.value] else None
                else:
                    sell_adv = utils[suit.value]
            else:
                sell_adv = None

            if buy_adv is not None and buy_adv > best_adv:
                best_action = 'bid'
                best_adv = buy_adv
                best_suit = suit

            if sell_adv is not None and sell_adv > best_adv:
                best_action = 'ask'
                best_adv = sell_adv
                best_suit = suit

            if buy_adv is not None and sell_adv is not None:
                at_adv = buy_adv + sell_adv
                if at_adv > best_adv:
                    best_action = 'at'
                    best_adv = at_adv
                    best_suit = suit

        return best_action, best_adv, best_suit

    def get_action(self, figgie: Figgie) -> Action:
        utils = self.calc_card_utils(self, figgie)
        best_transaction = self.get_best_transaction(figgie, utils)
        
        if best_transaction is not None:
            return best_transaction

        best_action, best_adv, best_suit = self.get_best_market_adv(figgie, utils)
        if best_action is not None:
            player = figgie.active_player
            market = figgie.markets[best_suit.value]
            if best_action == 'bid':
                bidding_price = int(self.buy_pricer.get_buying_price(figgie, best_suit, utils[best_suit.value]))
                if market.can_bid(player, bidding_price)[0]:
                    return Action.bid(best_suit, bidding_price)
                else:
                    return Action.passing()
            elif best_action == 'ask':
                asking_price = int(self.sell_pricer.get_selling_price(figgie, best_suit, utils[best_suit.value]))
                if market.can_ask(player, asking_price)[0]:
                    return Action.ask(best_suit, asking_price)
                else:
                    return Action.passing()
            elif best_action == 'at':
                bidding_price = int(self.buy_pricer.get_buying_price(figgie, best_suit, utils[best_suit.value]))
                asking_price = int(self.sell_pricer.get_selling_price(figgie, best_suit, utils[best_suit.value]))
                if market.can_at(player, bidding_price, asking_price)[0]:
                    return Action.at(best_suit, bidding_price, asking_price)
                else:
                    return Action.passing()
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

        return Action.passing()

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)


class UtilBuyPricer(BuyPricer):
    def get_buying_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        return max(round(card_util - 1), 1)


class UtilSellPricer(SellPricer):
    def get_selling_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        return max(round(card_util + 1), 1)


class MarketBuyPricer(BuyPricer):
    def get_buying_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        if market.has_buyer():
            return market.buying_price + 1
        else:
            return max(round(card_util - 1), 1)


class MarketSellPricer(SellPricer):
    def get_selling_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        if market.has_seller():
            return market.selling_price - 1
        else:
            return max(round(card_util + 1), 1)


class HalfBuyPricer(BuyPricer):
    def get_buying_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        minimum = market.buying_price if market.has_buyer() else 0
        return (round(card_util - minimum) // 2) + minimum


class HalfSellPricer(SellPricer):
    def get_selling_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        maximum = market.selling_price if market.has_seller() else round(card_util * 2)
        return maximum - (round(maximum - card_util) // 2)


class RandomBuyPricer(BuyPricer):
    def get_buying_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        return randint(market.buying_price + 1 if market.has_buyer() else 1, round(card_util))


class RandomSellPricer(SellPricer):
    def get_selling_price(self, figgie: Figgie, suit: Suit, card_util: float) -> int:
        market = figgie.markets[suit.value]
        return randint(round(card_util), market.selling_price - 1 if market.has_seller() else round(card_util * 2))