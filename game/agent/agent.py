from math import sqrt

from game.action.action import Action
from game.figgie import Figgie
from game.model.cheating_model import CheatingModel


class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0
        self.sum_x = 0
        self.sum_y = 0
        self.sum_xy = 0
        self.sum_x_squared = 0
        self.sum_y_squared = 0
        self.predictions = 0
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
        """
        Resets the agent's win statistics.
        """
        self.wins = 0
        self.total_utility = 0
        self.sum_x = 0
        self.sum_y = 0
        self.sum_xy = 0
        self.sum_x_squared = 0
        self.sum_y_squared = 0
        self.predictions = 0

    def add_prediction(self, model_prediction, actual) -> None:
        self.sum_x += model_prediction
        self.sum_y += actual
        self.sum_xy += model_prediction * actual
        self.sum_x_squared += model_prediction * model_prediction
        self.sum_y_squared += actual * actual
        self.predictions += 1

    def get_r_squared(self) -> float:
        if self.predictions == 0:
            return 0
        return (self.predictions * self.sum_xy - self.sum_x * self.sum_y) / sqrt((self.predictions * self.sum_x_squared - self.sum_x * self.sum_x) * (self.predictions * self.sum_y_squared - self.sum_y * self.sum_y))


