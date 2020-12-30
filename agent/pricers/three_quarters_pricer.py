from typing import Optional

import numpy as np

from agent.modular_agent import Pricer
from figgie import Figgie, Suit


class ThreeQuartersPricer(Pricer):
    def get_bidding_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        maximum = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        assert minimum <= maximum
        return 3 * (maximum - minimum) // 4 + minimum

    def get_asking_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        return self.get_asking_price_internal(market.selling_price, utils[suit.value])

    def get_asking_price_internal(self, market_price, util):
        minimum = max(1, round(util))
        maximum = market_price - 1 if market_price is not None else round(util * 2)
        assert minimum <= maximum
        return maximum - (maximum - minimum) // 4

    def get_at_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[tuple]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        high_bid = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        low_ask = round(utils[suit.value])
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        assert minimum <= high_bid <= low_ask <= maximum
        bidding_price = 3 * (high_bid - minimum) // 4 + minimum
        asking_price = maximum - (maximum - low_ask) // 4
        if asking_price == bidding_price:
            if bidding_price > minimum:
                bidding_price -= 1
            elif asking_price < maximum:
                asking_price += 1
            else:
                assert False, 'Market chooser should not select action where min util and max equal '
        return bidding_price, asking_price
