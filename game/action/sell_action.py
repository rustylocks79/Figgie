from game.action.action import Action
from game.suit import Suit


class SellAction(Action):
    def __init__(self, index: int, notes: str, suit: Suit):
        super().__init__(index, 'sell', notes)
        self.suit = suit

    def __str__(self):
        return 'agent {}: {} {}, {}'.format(self.index, self.operation, str(self.suit), self.notes)
