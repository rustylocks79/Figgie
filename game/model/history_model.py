import numpy as np

from game.figgie import Figgie
from game.model.simple_model import SimpleModel
from game.model.utility_model import UtilityModel
from game.suit import SUITS, Suit


class HistoryModel(UtilityModel):

    def get_total_seen(self, figgie: Figgie, index: int) -> np.ndarray:
        hand = figgie.cards[index]
        seen = np.full((4, 5), 0, dtype=int)

        for i, cards in enumerate(hand):
            seen[index][i] = cards
        seen[index][4] = 0

        for act in figgie.history:
            if act.operation == 'ask':
                if seen[act.index][act.suit.value] < 1:
                    seen[act.index][act.suit.value] = 1
            elif act.operation == 'buy':
                if seen[act.seller][act.suit.value] == 0:
                    seen[act.seller][act.suit.value] -= 1
                else:
                    seen[act.seller][4] -= 1
                seen[act.index][act.suit.value] += 1
            elif act.operation == 'sell':
                if seen[act.index][act.suit.value] == 0:
                    seen[act.index][act.suit.value] -= 1
                else:
                    seen[act.index][4] -= 1
                seen[act.buyer][act.suit.value] += 1
            elif act.operation == 'at':
                if seen[act.index][act.suit.value] < 1:
                    seen[act.index][act.suit.value] = 1

        total_seen = np.full(4, 0, dtype=int)
        for suit in SUITS:
            for i in range(4):
                total_seen[suit.value] += seen[i][suit.value]
        return total_seen

    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        hand = figgie.cards[index]
        total_seen = self.get_total_seen(figgie, index)
        if total_seen[suit.opposite().value] > 10:
            return 10 + (SimpleModel.get_expected_from_pot(hand[suit.value + 1]) - SimpleModel.get_expected_from_pot(suit.value))
        else:
            if total_seen[suit.value] > 10:
                return 0
            else:
                return .25 * (10 + (SimpleModel.get_expected_from_pot(hand[suit.value + 1]) - SimpleModel.get_expected_from_pot(suit.value)))