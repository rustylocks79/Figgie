from random import choice

from api.agent import Agent


class RandomAgent(Agent):
    def __init__(self, action_generator, action_mapper=None):
        super().__init__()
        self.action_generator = action_generator
        self.action_mapper = action_mapper

    def get_action(self, game) -> int:
        actions = self.action_generator(game)
        action = choice(actions)
        if self.action_mapper is not None:
            return self.action_mapper(game, action)
        else:
            return action