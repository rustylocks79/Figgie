import numpy as np

from game.figgie import Figgie
from game.model.simple_model import SimpleModel
from game.model.utility_model import UtilityModel
from game.suit import SUITS


class HistoryModel(UtilityModel):
    def get_expected_utility_change(self, figgie: Figgie, index: int, action) -> float:
        hand = figgie.cards[index].copy()
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

        for suit in SUITS:
            if total_seen[suit.value] > 10:
                goal_suit = suit.opposite()
                current_expected_util = 10 * hand[goal_suit.value] + SimpleModel.get_expected_from_pot(hand[goal_suit.value])
                if action is not None and action.suit == goal_suit:
                    if action.operation == 'buy':
                        hand[action.suit.value] += 1
                    elif action.operation == 'sell':
                        hand[action.suit.value] -= 1
                    else:
                        assert False, 'Invalid operation: {}'.format(str(action))
                new_expected_util = 10 * hand[goal_suit.value] + SimpleModel.get_expected_from_pot(hand[goal_suit.value])
                return new_expected_util - current_expected_util

        total = sum(total_seen)
        current_exp_util = SimpleModel.get_expected_util(hand, np.array([total_seen[0] / total,
                                                                         total_seen[1] / total,
                                                                         total_seen[2] / total,
                                                                         total_seen[3] / total], dtype=float))
        if action is not None:
            if action.operation == 'buy':
                hand[action.suit.value] += 1
            elif action.operation == 'sell':
                hand[action.suit.value] -= 1
            else:
                assert False, 'Invalid operation: {}'.format(str(action))

        new_exp_util = SimpleModel.get_expected_util(hand, np.array([total_seen[0] / total,
                                                                     total_seen[1] / total,
                                                                     total_seen[2] / total,
                                                                     total_seen[3] / total], dtype=float))

        return new_exp_util - current_exp_util
