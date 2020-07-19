from random import choice

from my_math import choice_weighted


class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0

    def get_action(self, game) -> int:
        pass


class ControllerAgent(Agent):
    def get_action(self, game) -> int:
        return input('Action: ')


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


class OneActionAgent(Agent):
    def __init__(self, action: int):
        super().__init__()
        self.action = action

    def get_action(self, game) -> int:
        return self.action


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
            action = actions[choice_weighted(self.strategy[info_set])]
        else:
            self.unknown_states += 1
            action = choice(actions)
        if self.action_mapper is not None:
            return self.action_mapper(game, action)
        else:
            return action