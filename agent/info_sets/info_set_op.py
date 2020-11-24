from agent.info_sets.info_set_std import InfoSetStd
from figgie import Figgie, Suit


class InfoSetOP(InfoSetStd):
    def __init__(self):
        super().__init__('op')

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.opposite().value]
        result = super().generate_info_set(figgie, card_util, target_operation, target_suit) + ','
        if target_operation == 'ask':
            result += market.selling_price
        elif target_operation == 'bid':
            result += market.buying_price
        elif target_operation == 'at':
            result += market.buying_price + ', ' + market.selling_price
        else:
            raise RuntimeError('Invalid operation: {}'.format(target_operation))
        return result
