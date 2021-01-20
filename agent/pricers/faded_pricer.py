from typing import Optional

import numpy as np

from agent.modular_agent import Pricer
from figgie import Figgie, Suit


class FadedPricer(Pricer):
    def get_bidding_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        maximum = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        if market.last_price is not None and minimum < market.last_price < maximum:
            maximum = market.last_price
        assert minimum <= maximum
        return (maximum - minimum) // 2 + minimum

    def get_asking_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[int]:
        market = figgie.markets[suit.value]
        minimum = max(1, round(utils[suit.value]))
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        if market.last_price is not None and minimum < market.last_price < maximum:
            minimum = market.last_price
        assert minimum <= maximum
        return maximum - (maximum - minimum) // 2

    def get_at_price(self, figgie: Figgie, suit: Suit, utils: np.ndarray) -> Optional[tuple]:
        market = figgie.markets[suit.value]
        minimum = market.buying_price + 1 if market.has_buyer() else 1
        high_bid = min(round(utils[suit.value]), figgie.chips[figgie.active_player])
        low_ask = round(utils[suit.value])
        maximum = market.selling_price - 1 if market.has_seller() else round(utils[suit.value] * 2)
        if market.last_price is not None:
            if minimum < market.last_price < high_bid:
                high_bid = market.last_price
            elif low_ask < market.last_price < maximum:
                low_ask = market.last_price
        assert minimum <= high_bid <= low_ask <= maximum
        bidding_price = (high_bid - minimum) // 2 + minimum
        asking_price = maximum - (maximum - low_ask) // 2
        if asking_price == bidding_price:
            if bidding_price > minimum:
                bidding_price -= 1
            elif asking_price < maximum:
                asking_price += 1
            else:
                assert False, 'Market chooser should not select action where min util and max equal '
        return bidding_price, asking_price
