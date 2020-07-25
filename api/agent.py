class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0

    def get_action(self, game) -> int:
        pass

    def reset(self) -> None:
        self.wins = 0
        self.total_utility = 0
