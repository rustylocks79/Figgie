from random import choice

import numpy as np

from api.agent import Agent


class StrategyAgent(Agent):
    def __init__(self, strategy: dict, info_set_generator, action_generator, action_mapper=None):
        super().__init__()
        self.strategy = strategy
        self.info_set_generator = info_set_generator
        self.unknown_states = 0
        self.action_generator = action_generator
        self.action_mapper = action_mapper

    def get_action(self, game) -> int:
        info_set = self.info_set_generator(game)
        actions = self.action_generator(game)
        if info_set in self.strategy:
            action = np.random.choice(actions, p=self.strategy[info_set])
        else:
            self.unknown_states += 1
            action = choice(actions)
        if self.action_mapper is not None:
            return self.action_mapper(game, action)
        else:
            return action
