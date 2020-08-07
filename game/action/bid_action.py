from game.action.action import Action
from game.suit import Suit


class BidAction(Action):
    def __init__(self, suit: Suit, buying_price: int, notes: str = ''):
        super().__init__('bid', notes)
        self.suit = suit
        self.buying_price = buying_price

    def __str__(self):
        return 'agent {}: {} {} {}, {}'.format(self.index, self.operation, str(self.suit), self.buying_price,
                                               self.notes)