from game.figgie import Suit, Figgie


class UtilityModel:
    def get_expected_utility(self, figgie: Figgie, index: int, action=None):
        """
        :param figgie: the current game
        :param index: the index of the current agent
        :param action: a potential action taken by the player
        :return: the utility the player should expect to receive if the game ended after this action
        """
        pass
