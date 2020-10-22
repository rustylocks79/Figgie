import numpy as np

from figgie import SUITS, Figgie


class SimpleChooser:
    def get_best_market_adv(self, figgie: Figgie, utils: np.ndarray) -> tuple:
        player = figgie.active_player
        best_action = None
        best_adv = 0
        best_suit = None
        for suit in SUITS:
            market = figgie.markets[suit.value]
            util = round(utils[suit.value])

            # Get Bidding Advantage
            if market.has_buyer():
                minimum = market.buying_price + 1
                maximum = min(utils[suit.value], figgie.chips[player])
                buy_adv = maximum - minimum if maximum > minimum else None
            else:
                buy_adv = util - 1

            # Get Asking Advantage
            if figgie.cards[player][suit.value] >= 1:
                if market.has_seller():
                    minimum = util
                    maximum = market.selling_price - 1
                    sell_adv = maximum - minimum if maximum > minimum else None
                else:
                    sell_adv = util
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
