from game.action.action import Action
from game.suit import Suit


class BuyAction(Action):
    def __init__(self, index: int, notes: str, suit: Suit):
        super().__init__(index, 'buy', notes)
        self.suit = suit
        self.seller = None

    def __str__(self):
        return 'agent {}: {} {}, {}'.format(self.index, self.operation, str(self.suit), self.notes)
