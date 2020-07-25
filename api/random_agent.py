from random import choice

from api.agent import Agent


class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def get_action(self, game) -> int:
        return choice(game.get_actions())
