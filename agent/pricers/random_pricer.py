from random import randint

import numpy as np

from agent.modular_agent import Pricer
from figgie import Figgie, Suit


class RandomPricer(Pricer):
    def get_bidding_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> int:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        return randint(minimum, round(utils[suit.value]))

    def get_asking_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> int:
        market = figgie.markets[suit.value]
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        return randint(round(utils[suit.value]), maximum)

    def get_at_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> tuple:
        bidding_price = self.get_bidding_price(figgie, suit, utils)
        asking_price = self.get_asking_price(figgie, suit, utils)
        if bidding_price >= asking_price:
            market = figgie.markets[suit.value]
            minimum = market.buying_price if market.has_buyer() else 1
            maximum = market.selling_price if market.has_seller() else None
            diff = bidding_price - asking_price + 1
            if bidding_price - diff > minimum + 1:
                bidding_price -= diff
            elif maximum is None or asking_price + diff < maximum - 1:
                asking_price += diff
            else:
                return None
        return bidding_price, asking_price
