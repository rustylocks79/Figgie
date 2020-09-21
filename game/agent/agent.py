from math import sqrt

from game.action.action import Action
from game.figgie import Figgie
from game.model.cheating_model import CheatingModel


class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0
        self.total_error = 0
        self.trails = 0
        self.cheating_model = CheatingModel()

    def get_action(self, figgie: Figgie) -> Action:
        """
        :param figgie: the current game.
        :return: an action to be preformed by the agent in the game figgie
        """
        pass

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        pass

    def reset(self) -> None:
        pass

    def clear(self) -> None:
        """
        Resets the agent's win statistics.
        """
        self.wins = 0
        self.total_utility = 0
        self.total_error = 0
        self.trails += 0

    def add_prediction(self, model_prediction, actual) -> None:
        self.total_error += pow(actual - model_prediction, 2)
        self.trails += 1

    def get_rmse(self) -> float:
        if self.trails == 0:
            return 0
        return sqrt(self.total_error / self.trails)


