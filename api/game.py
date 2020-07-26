import numpy as np


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

    def get_actions(self) -> np.ndarray:
        pass

    def get_action_text(self, action: int) -> str:
        pass

    def preform(self, action: int) -> None:
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

    def get_utility(self) -> list:
        """
        Precondition: the game must be in a terminal state.
        Returns the utility achieved by all players.
        """
        pass

    def play(self, agents: list, trials: int, verbose=False):
        for i in range(trials):
            while not self.is_finished():
                player = self.get_active_player()
                action = agents[player].get_action(self)
                if verbose:
                    print('agent {}: {}'.format(player, self.get_action_text(action)))
                self.preform(action)
            utility = self.get_utility()
            for j, agent in enumerate(agents):
                agent.total_utility += utility[j]
            max_utility = max(utility)
            winners = [j for j in range(len(utility)) if utility[j] == max_utility]
            for winner in winners:
                agents[winner].wins += 1
            self.reset()
