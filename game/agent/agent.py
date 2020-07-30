from game.action.action import Action
from game.figgie import Figgie


class Agent:
    def __init__(self, index: int):
        self.index = index
        self.wins = 0
        self.total_utility = 0

    def get_action(self, figgie: Figgie) -> Action:
        pass

    def reset(self) -> None:
        self.wins = 0
        self.total_utility = 0
