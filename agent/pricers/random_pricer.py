from random import randint
from typing import Optional

import numpy as np

from agent.modular_agent import Pricer
from figgie import Figgie, Suit


class RandomPricer(Pricer):
    def get_bidding_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        maximum = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        assert minimum <= maximum
        return randint(minimum, maximum)

    def get_asking_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        minimum = round(utils[suit.value])
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        assert minimum <= maximum
        return randint(minimum, maximum)

    def get_at_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[tuple]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        high_bid = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        low_ask = round(utils[suit.value])
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        assert minimum <= high_bid <= low_ask <= maximum
        bidding_price = randint(minimum, high_bid)
        asking_price = randint(low_ask, maximum)
        if asking_price == bidding_price:
            if bidding_price > minimum:
                bidding_price -= 1
            elif asking_price < maximum:
                asking_price += 1
            else:
                assert False, 'Market chooser should not select action where min util and max equal '
        return bidding_price, asking_price
