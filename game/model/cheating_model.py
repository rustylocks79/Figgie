from game.figgie import Figgie, NUM_PLAYERS
from game.model.utility_model import UtilityModel
from game.suit import Suit


class CheatingModel(UtilityModel):
    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        player = figgie.active_player
        hand = figgie.cards[player]
        market = figgie.markets[suit.value]

        if suit == figgie.goal_suit:
            new_cards = figgie.cards.copy()
            if market.is_seller() and market.selling_player != index:
                # if there is a seller in the market then evaluate the card based on buying the card from that player.
                new_cards[market.selling_player][suit.value] -= 1
            else:
                # if no one is buying make the assumption that the player with the least number of cards (at least one) in that suit is selling.
                min_player = 0
                min_cards = 13
                for i in range(3):
                    if 0 < figgie.cards[i][suit.value] < min_cards:
                        min_player = i
                        min_cards = figgie.cards[i][suit.value]
                new_cards[min_player][suit.value] -= 1
            new_cards[index][suit.value] += 1
            return 10 + (self.get_expected_from_pot(figgie, new_cards) - self.get_expected_from_pot(figgie, figgie.cards))
        else:
            return 0

    def get_expected_from_pot(self, figgie, cards) -> float:
        player = figgie.active_player
        cards_in_goal_suit = sum(figgie.cards[i][figgie.goal_suit.value] for i in range(4))
        # assert cards_in_goal_suit == 8 or cards_in_goal_suit == 10, 'cards in goal suit must equal 8 or 10'
        max_goal_cards = max(cards[i][figgie.goal_suit.value] for i in range(NUM_PLAYERS))
        winners = [j for j in range(NUM_PLAYERS) if cards[j][figgie.goal_suit.value] == max_goal_cards]
        if player in winners:
            return (200 - (cards_in_goal_suit * 10)) // len(winners)
        else:
            return 0
