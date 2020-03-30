from math import floor

from figgie import *
from random import *


def get_random_suit() -> Suit:
    return choice(SUITS)


class SimplePlayer(Player):
    def __init__(self, name, game, buy_tolerance=1, sell_tolerance=1):
        super().__init__(name, game)
        self.seen = []
        self.ranges = {}
        self.buy_tolerance = buy_tolerance
        self.sell_tolerance = sell_tolerance

    def get_total_seen(self):
        return sum([self.seen[suit] for suit in SUITS])

    def get_ranges(self) -> dict:
        result = {}
        total_seen = self.get_total_seen()
        for suit in SUITS:
            expected_value = floor((self.seen[suit] / total_seen) * 10)
            result[suit] = (max(expected_value - self.sell_tolerance, 1), min(expected_value + self.buy_tolerance, 10))
        return result

    def on_deal(self):
        self.seen = self.cards.copy()

    def get_best_deal(self):
        best_suit = None
        best_action = None
        best_adv = -1
        for suit in SUITS:
            # attempt to sell cards
            if self.get_buying_price(suit) is not None and self.get_buying_player(suit) is not self:
                sell_adv = self.get_buying_price(suit) - self.ranges[suit][0]  # adv = [market buying price] - [min selling price]
                # print('\tselling advantage for {}, sellAdv: {}, market buy price {}, min selling price {}'
                #       .format(suit.name, sell_adv, self.get_buying_price(suit), self.ranges[suit][0]))
                if sell_adv > best_adv:
                    best_adv = sell_adv
                    best_suit = suit
                    best_action = 'sell'

            # attempt to buy cards
            if self.get_selling_price(suit) is not None and self.get_selling_player(suit) is not self:
                buy_adv = self.ranges[suit][1] - self.get_selling_price(suit)  # adv = [max buying price] - [market selling price]
                # print('\tbuying advantage for {}, buyAdv: {}, market sell price {}, max buy price {}'
                #       .format(suit.name, buy_adv, self.get_selling_price(suit), self.ranges[suit][1]))
                if buy_adv > best_adv:
                    best_adv = buy_adv
                    best_suit = suit
                    best_action = 'buy'

        # if best_suit is not None:
        #     print('{}, {}'.format(best_suit.name, best_action))
        return best_suit, best_action

    def on_turn(self, verbose=False):
        if verbose:
            print('{}\'s turn: '.format(self.name))

        self.ranges = self.get_ranges()
        best_suit, best_action = self.get_best_deal()
        if best_suit is not None:
            if best_action == 'buy':
                self.buy(best_suit, verbose)
            else:
                self.sell(best_suit, verbose)
        else:
            while True:
                suit = get_random_suit()
                if self.cards[suit] > 0:
                    self.at(suit, self.ranges[suit][0], self.ranges[suit][1], verbose)
                    break
        if verbose:
            print()

