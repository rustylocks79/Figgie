from game.figgie import Suit, Figgie


class UtilityModel:
    def get_expected_utility_change(self, figgie: Figgie, index: int, action) -> float:
        """
        :param figgie: the current game
        :param index: the index of the current agent
        :param action: a potential action taken by the player
        :return: the utility the player should expect to receive if the game ended after this action
        """
        pass
