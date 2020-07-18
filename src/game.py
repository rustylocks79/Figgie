from random import choice


class Agent:
    def __init__(self):
        self.wins = 0
        self.total_utility = 0

    def get_action(self, game) -> str:
        pass


class ControllerAgent(Agent):
    def get_action(self, game) -> str:
        return input('Action: ')


class RandomAgent(Agent):
    def get_action(self, game) -> str:
        actions = game.get_actions()
        return choice(actions)


class OneActionAgent(Agent):
    def __init__(self, action):
        super().__init__()
        self.action = action

    def get_action(self, game) -> str:
        return self.action


class Game:
    def reset(self) -> None:
        """
        Resets the game to a start state.
        """
        pass

    def get_active_player(self) -> int:
        """
        :return: the active player in the games current state.
        """
        pass

    def get_actions(self) -> list:
        """
        :return: a list of string actions that can be preformed in the games current state.
        """
        pass

    def preform(self, action: str) -> None:
        """
        :param action: the string action to be preformed
        :return: change the state of the game by preforming the provided action.
        """
        pass

    def is_finished(self) -> bool:
        """
        Returns True if the game is in a terminal state, False otherwise.
        """
        pass

    def get_utility(self, player: int) -> int:
        """
        Precondition: the game must be in a terminal state.
        Returns the utility achieved by player with the index 'player_index'.
        :param player: the index of a player
        """
        pass

    def play(self, agents: list, trials: int):
        for i in range(trials):
            while not self.is_finished():
                player = self.get_active_player()
                self.preform(agents[player].get_action(self))
            max_index = 0
            max_utility = self.get_utility(0)
            agents[0].total_utility += max_utility
            for j in range(1, len(agents)):
                utility = self.get_utility(j)
                agents[j].total_utility += utility
                if utility > max_utility:
                    max_index = j
                    max_utility = utility
            agents[max_index].wins += 1
            self.reset()
