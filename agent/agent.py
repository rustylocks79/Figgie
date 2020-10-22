import numpy as np

from figgie import Figgie, Action


class Agent:
    def __init__(self, name, collector=False):
        self.name = name
        self.wins = 0
        self.total_utility = 0
        self.total_error = 0
        self.trails = 0
        self.operations = {}
        self.training_data = []
        self.collector = collector

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

    def collect(self, figgie: Figgie):
        if self.collector:
            self.training_data.append((
                np.array([
                    [cards for cards in figgie.cards[figgie.active_player]],
                    [market.buying_price if market.buying_price is not None else 0 for market in figgie.markets],
                    [market.selling_price if market.selling_price is not None else 0 for market in figgie.markets],
                    [market.last_price if market.last_price is not None else 0 for market in figgie.markets],
                    [market.operations for market in figgie.markets],
                    [market.transactions for market in figgie.markets],
                ], dtype=np.float32).flatten(), figgie.goal_suit.value
            ))

    def get_avg_operations(self, trials) -> dict:
        result = {}
        for key in self.operations:
            result[key] = self.operations[key] / trials
        return result
