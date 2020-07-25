from api.agent import Agent


class OneActionAgent(Agent):
    def __init__(self, action: int):
        super().__init__()
        self.action = action

    def get_action(self, game) -> int:
        return self.action