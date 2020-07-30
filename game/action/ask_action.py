from game.action.action import Action
from game.suit import Suit


class AskAction(Action):
    def __init__(self, index: int, notes: str, suit: Suit, selling_price: int):
        super().__init__(index, 'ask', notes)
        self.suit = suit
        self.selling_price = selling_price

    def __str__(self):
        return 'agent {}: {} {} {}, {}'.format(self.index, self.operation, str(self.suit), self.selling_price, self.notes)