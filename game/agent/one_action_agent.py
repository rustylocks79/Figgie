from game.agent.agent import Agent
from game.figgie import Figgie


class OneActionAgent(Agent):
    def __init__(self, index: int, action: tuple):
        super().__init__(index)
        self.action = action

    def get_action(self, figgie: Figgie) -> tuple:
        return self.action