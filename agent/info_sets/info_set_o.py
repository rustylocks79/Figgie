from agent.info_sets.info_set_std import InfoSetStd
from figgie import Figgie, Suit


class InfoSetO(InfoSetStd):
    def __init__(self):
        super().__init__('o')

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + str(market.operations)