import numpy as np

from agent.models.utility_model import UtilityModel
from figgie import Figgie, NUM_PLAYERS


class CheatingModel(UtilityModel):
    def __init__(self):
        super().__init__('cheating')

    def get_card_utility(self, figgie: Figgie, index: int) -> np.ndarray:
        player = figgie.active_player
        hand = figgie.cards[player]
        market = figgie.markets[figgie.goal_suit.value]
        result = np.full(4, 0, dtype=float)
        new_cards = figgie.cards.copy()

        if market.has_seller() and market.selling_player != index:
            # if there is a seller in the market then evaluate the card based on buying the card from that player.
            new_cards[market.selling_player][figgie.goal_suit.value] -= 1
        else:
            # if no one is buying make the assumption that the player with the least number of cards (at least one) in that suit is selling.
            min_player = 0
            min_cards = 13
            for i in range(3):
                if 0 < figgie.cards[i][figgie.goal_suit.value] < min_cards:
                    min_player = i
                    min_cards = figgie.cards[i][figgie.goal_suit.value]
            new_cards[min_player][figgie.goal_suit.value] -= 1
        new_cards[index][figgie.goal_suit.value] += 1

        value = (self.get_expected_from_pot(figgie, new_cards) - self.get_expected_from_pot(figgie, figgie.cards))
        result[figgie.goal_suit.value] = value
        return result

    @staticmethod
    def get_expected_from_pot(figgie, cards) -> float:
        player = figgie.active_player
        cards_in_goal_suit = sum(figgie.cards[i][figgie.goal_suit.value] for i in range(4))
        max_goal_cards = max(cards[i][figgie.goal_suit.value] for i in range(NUM_PLAYERS))
        winners = [j for j in range(NUM_PLAYERS) if cards[j][figgie.goal_suit.value] == max_goal_cards]
        if player in winners:
            return cards[player][figgie.goal_suit.value] * 10 + (200 - (cards_in_goal_suit * 10)) // len(winners)
        else:
            return cards[player][figgie.goal_suit.value] * 10
