

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

    def play(self, agents: list, trials: int):
        for i in range(trials):
            while not self.is_finished():
                player = self.get_active_player()
                self.preform(agents[player].get_action(self))
            utility = self.get_utility()
            for i in range(len(agents)):
                agents[i].total_utility += utility[i]
            max_utility = max(utility)
            winners = [j for j in range(len(utility)) if utility[j] == max_utility]
            for winner in winners:
                agents[winner].wins += 1
            self.reset()
