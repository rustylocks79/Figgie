from typing import Optional

import numpy as np

from agent.agent import Agent
from agent.models.utility_model import UtilityModel
from figgie import Figgie, Suit, Action, SUITS


class Pricer:
    def get_bidding_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        pass

    def get_asking_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        pass

    def get_at_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[tuple]:
        pass


class ModularAgent(Agent):
    def __init__(self, model: UtilityModel, pricer: Pricer):
        super().__init__('Modular Agent')
        self.util_model = model
        self.pricer = pricer

    def reset(self) -> None:
        super().reset()
        self.util_model.reset()

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
        player = figgie.active_player
        utils = self.util_model.get_card_utility(figgie, player)
        actual_utils = self.cheating_model.get_card_utility(figgie, player)
        self.add_prediction(utils, actual_utils)
        best_transaction = self.get_best_transaction(figgie, utils)
        
        if best_transaction is not None:
            return best_transaction

        best_action, best_adv, best_suit = self.get_best_market_adv(figgie, utils)
        if best_action is not None:
            if best_action == 'bid':
                bidding_price = self.pricer.get_bidding_price(figgie, best_suit, utils)
                if bidding_price is not None:
                    return Action.bid(best_suit, bidding_price)
            elif best_action == 'ask':
                asking_price = self.pricer.get_asking_price(figgie, best_suit, utils)
                if asking_price is not None:
                    return Action.ask(best_suit, asking_price)
            elif best_action == 'at':
                price = self.pricer.get_at_price(figgie, best_suit, utils)
                if price is not None:
                    return Action.at(best_suit, price[0], price[1])
            else:
                raise ValueError('Best action can not be: {}'.format(best_action))

        return Action.passing()

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)
