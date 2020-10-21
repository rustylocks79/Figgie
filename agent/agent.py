from math import sqrt

import numpy as np

from agent.models.cheating_model import CheatingModel
from figgie import Figgie, Action


class Agent:
    def __init__(self, name):
        self.name = name
        self.wins = 0
        self.total_utility = 0
        self.total_error = 0
        self.trails = 0
        self.cheating_model = CheatingModel()
        self.operations = {}

    def get_action(self, figgie: Figgie) -> Action:
        """
        :param figgie: the current game.
        :return: an action to be preformed by the agent in the game figgie
        """
        pass

    def add_operation(self, action: Action):
        if action.operation in self.operations:
            self.operations[action.operation] += 1
        else:
            self.operations[action.operation] = 1

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        pass

    def reset(self) -> None:
        pass

    def add_prediction(self, model_utils: np.ndarray, actual_utils: np.ndarray) -> None:
        for i in range(len(model_utils)):
            self.total_error += pow(actual_utils[i] - model_utils[i], 2)
        self.trails += len(model_utils)

    def get_rmse(self) -> float:
        if self.trails == 0:
            return 0
        return sqrt(self.total_error / self.trails)

    def get_avg_operations(self, trials) -> dict:
        result = {}
        for key in self.operations:
            result[key] = self.operations[key] / trials
        return result



