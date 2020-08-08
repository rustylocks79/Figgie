from game.action.action import Action
from game.figgie import Figgie


class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0

    def get_action(self, figgie: Figgie) -> Action:
        """
        :param figgie: the current game.
        :return: an action to be preformed by the agent in the game figgie
        """
        pass

    def reset(self) -> None:
        """
        Resets the agent's win statistics.
        """
        self.wins = 0
        self.total_utility = 0
