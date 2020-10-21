from agent.agent import Agent
from figgie import Action
from figgie import Figgie


class OneActionAgent(Agent):
    def __init__(self, index: int, action: Action):
        super().__init__(index)
        self.action = action

    def get_action(self, figgie: Figgie) -> Action:
        return self.action
