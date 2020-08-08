from game.figgie import Figgie
from game.model.utility_model import UtilityModel
from game.suit import Suit

PROBABILITY_8_CARD_GOAL_SUIT = .33
PROBABILITY_10_CARD_GOAL_SUIT = .67
CHANCE_TO_WIN = .5  # TODO: .5 is an arbitrary value


class SimpleModel(UtilityModel):

    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        hand = figgie.cards[index]
        if hand[suit.opposite().value] > 10:
            return 10 + (self.get_expected_from_pot(hand[suit.value + 1]) - self.get_expected_from_pot(suit.value))
        else:
            if hand[suit.value] > 10:
                return 0
            else:
                return .25 * (10 + (self.get_expected_from_pot(hand[suit.value + 1]) - self.get_expected_from_pot(suit.value)))

    @staticmethod
    def get_expected_from_pot(cards: int):
        """
        :param cards: the number of cards the agent has of one suit
        :return: the expected utility the agent will receive from the pot should this suit be the goal suit.
        """
        if cards > 10:
            return 0
        elif cards > 8:
            return 100
        elif cards >= 6:
            return PROBABILITY_8_CARD_GOAL_SUIT * 120 + PROBABILITY_10_CARD_GOAL_SUIT * 100
        elif cards == 5:
            return PROBABILITY_8_CARD_GOAL_SUIT * 100 + PROBABILITY_10_CARD_GOAL_SUIT * (50 + CHANCE_TO_WIN * 50)
        else:
            return CHANCE_TO_WIN * (.33 * 120 + .67 * 100)
