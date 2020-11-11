from agent.info_sets.info_set_std import InfoSetStd
from figgie import Figgie, Suit


class InfoSetL(InfoSetStd):
    def __init__(self):
        super().__init__('l')

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        last_transaction = figgie.markets[target_suit.value].last_price
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + str(last_transaction)