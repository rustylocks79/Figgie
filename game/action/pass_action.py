from game.action.action import Action


class PassAction(Action):
    def __init__(self, notes: str = ''):
        super().__init__('pass', notes)

    def __str__(self):
        return 'agent {}: {}, {}'.format(self.index, self.operation, self.notes)
