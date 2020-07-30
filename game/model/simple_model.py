from game.figgie import Suit, Figgie, SUITS
from game.model.utility_model import UtilityModel


class SimpleModel(UtilityModel):
    def get_expected_utility(self, figgie: Figgie, index: int, action=None):
        operation = None
        action_suit = None
        if action is not None:
            operation = action[0]
            action_suit = action[1]
        hand = figgie.cards[index].copy()
        expected_util = figgie.chips[index]
        if action is not None:
            market = figgie.markets[action_suit.value]
            if operation == 'buy':
                expected_util -= market.selling_price
                hand[action_suit.value] += 1
            elif operation == 'sell':
                expected_util += market.buying_price
                hand[action_suit.value] -= 1
            else:
                assert False, 'Invalid operation: {}'.format(operation)

        for suit in SUITS:
            if hand[suit.value] > 10:
                return expected_util + 10 * hand[suit.value] + self.get_expected_from_pot(hand[suit.value])

        for suit in SUITS:
            expected_util += .25 * (hand[suit.value] * 10 + self.get_expected_from_pot(hand[suit.value]))
        return expected_util

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