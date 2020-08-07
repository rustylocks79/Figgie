import numpy as np

from game.figgie import Figgie, SUITS
from game.model.utility_model import UtilityModel


class SimpleModel(UtilityModel):

    def get_expected_utility_change(self, figgie: Figgie, index: int, action) -> float:
        hand = figgie.cards[index].copy()

        for suit in SUITS:
            if hand[suit.value] > 10:
                goal_suit = suit.opposite()
                current_expected_util = 10 * hand[goal_suit.value] + self.get_expected_from_pot(hand[goal_suit.value])
                if action is not None and action.suit == goal_suit:
                    if action.operation == 'buy':
                        hand[action.suit.value] += 1
                    elif action.operation == 'sell':
                        hand[action.suit.value] -= 1
                    else:
                        assert False, 'Invalid operation: {}'.format(str(action))
                new_expected_util = 10 * hand[goal_suit.value] + self.get_expected_from_pot(hand[goal_suit.value])
                return new_expected_util - current_expected_util

        current_exp_util = SimpleModel.get_expected_util(hand, np.array([.25, .25, .25, .25], dtype=float))
        if action is not None:
            if action.operation == 'buy':
                hand[action.suit.value] += 1
            elif action.operation == 'sell':
                hand[action.suit.value] -= 1
            else:
                assert False, 'Invalid operation: {}'.format(str(action))

        new_exp_util = SimpleModel.get_expected_util(hand, np.array([.25, .25, .25, .25], dtype=float))
        return new_exp_util - current_exp_util

    @staticmethod
    def get_expected_util(hand: np.ndarray, probabilities: np.ndarray):
        result = 0
        for i, prob in enumerate(probabilities):
            result += prob * (hand[i] * 10 + SimpleModel.get_expected_from_pot(hand[i]))
        return result

    @staticmethod
    def get_expected_from_pot(cards: int):
        if cards > 10:
            return 0
        elif cards > 8:
            return 100
        if cards >= 6:
            return .33 * 120 + .67 * 100
        if cards >= 5:
            return .33 * (60 + .5 * 60) + .67 * (50 + .5 * 50)  # TODO: .5 is an arbitrary value
        else:
            return .5 * (.33 * 120 + .67 * 100)  # TODO: .5 is an arbitrary value
