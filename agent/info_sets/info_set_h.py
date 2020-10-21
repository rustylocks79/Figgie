from agent.info_sets.info_set_std import InfoSetStd
from figgie import Figgie, Suit


class InfoSetH(InfoSetStd):
    def __init__(self):
        super().__init__('h')

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        player = figgie.active_player
        hand = figgie.cards[figgie.active_player]
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + str(hand[player])