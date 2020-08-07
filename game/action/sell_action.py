from game.action.action import Action
from game.suit import Suit


class SellAction(Action):
    def __init__(self, suit: Suit, notes: str = ''):
        super().__init__('sell', notes)
        self.suit = suit
        self.buyer = None

    def __str__(self):
        return 'agent {}: {} {}, {}'.format(self.index, self.operation, str(self.suit), self.notes)
