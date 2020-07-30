from game.action.action import Action
from game.suit import Suit


class PassAction(Action):
    def __init__(self, index: int, notes: str):
        super().__init__(index, 'pass', notes)

    def __str__(self):
        return 'agent {}: {}, {}'.format(self.index, self.operation, self.notes)
