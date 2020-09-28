import numpy as np

from game.action.action import Action
from game.figgie import Figgie
from game.model.simple_model import SimpleModel
from game.model.utility_model import UtilityModel
from game.suit import SUITS, Suit


class HistoryModel(UtilityModel):

    def __init__(self):
        super().__init__('history')
        self.seen = np.full((4, 5), 0, dtype=int)
        for i in range(4):
            self.seen[i][4] = 10
        self.first = True

    def get_total_seen(self, figgie: Figgie, index: int) -> np.ndarray:
        total_seen = np.full(4, 0, dtype=int)
        for suit in SUITS:
            for i in range(4):
                total_seen[suit.value] += self.seen[i][suit.value]
        return total_seen

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        if action.operation == 'ask':
            if self.seen[action.index][action.suit.value] < 1:
                self.seen[action.index][action.suit.value] = 1
        elif action.operation == 'buy':
            if self.seen[action.seller][action.suit.value] == 0:
                self.seen[action.seller][action.suit.value] -= 1
            else:
                self.seen[action.seller][4] -= 1
            self.seen[action.index][action.suit.value] += 1
        elif action.operation == 'sell':
            if self.seen[action.index][action.suit.value] == 0:
                self.seen[action.index][action.suit.value] -= 1
            else:
                self.seen[action.index][4] -= 1
            self.seen[action.buyer][action.suit.value] += 1
        elif action.operation == 'at':
            if self.seen[action.index][action.suit.value] < 1:
                self.seen[action.index][action.suit.value] = 1

    def reset(self):
        self.seen = np.full((4, 5), 0, dtype=int)
        for i in range(4):
            self.seen[i][4] = 10
        self.first = True

    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        hand = figgie.cards[index]
        if self.first:
            for i, cards in enumerate(hand):
                self.seen[index][i] = cards
            self.seen[index][4] = 0

        total_seen = self.get_total_seen(figgie, index)
        if total_seen[suit.opposite().value] > 10:
            return 10 + (SimpleModel.get_expected_from_pot(hand[suit.value + 1]) - SimpleModel.get_expected_from_pot(suit.value))
        else:
            if total_seen[suit.value] > 10:
                return 0
            else:
                return .25 * (10 + (SimpleModel.get_expected_from_pot(hand[suit.value + 1]) - SimpleModel.get_expected_from_pot(suit.value)))