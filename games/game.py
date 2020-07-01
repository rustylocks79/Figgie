class Game:
    def reset(self) -> None:
        """
        Resets the game to a start state.
        """
        pass

    def get_actions(self) -> list:
        pass

    def preform(self, action: str):
        pass

    def is_finished(self) -> bool:
        """
        Returns True if the game is in a terminal state, False otherwise.
        """
        pass

    def get_utility(self, player_index: int) -> int:
        """
        Precondition: the game must be in a terminal state.
        Returns the utility achieved by player with the index 'player_index'.
        :param player_index: the index of a player
        """
        pass
