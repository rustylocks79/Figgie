import numpy as np

from agent.regret_agent import InfoSetGenerator
from figgie import Figgie, Suit


class InfoSetStd(InfoSetGenerator):
    def __init__(self, name):
        super().__init__(name)

    def generate_info_set(self, figgie: Figgie, card_util: int, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        if target_operation == 'bid':
            return 'bid,{},{}'.format(card_util, market.buying_price if market.has_buyer() else 'N')
        elif target_operation == 'ask':
            return 'ask,{},{}'.format(card_util, market.selling_price if market.has_seller() else 'N')
        elif target_operation == 'at':
            return 'at,{},{},{}'.format(card_util, market.buying_price if market.has_buyer() else 'N',
                                        market.selling_price if market.has_seller() else 'N')
        else:
            raise ValueError("Invalid action: {}".format(target_operation))

    def generate_bid_actions(self, card_util: float, buying_price: int, target_suit: Suit) -> np.ndarray:
        min_buy = buying_price + 1 if buying_price is not None else 1
        return np.arange(min_buy, min_buy + 8, dtype=np.int32)

    def generate_ask_actions(self, card_util: float, selling_price: int, target_suit: Suit) -> np.ndarray:
        max_sell = selling_price if selling_price is not None else int(card_util) + 8
        return np.arange(max(max_sell - 8, 1), max_sell, dtype=np.int32)

    def generate_at_actions(self, card_util: float, buying_price: int, selling_price: int, target_suit: Suit) -> np.ndarray:
        actions = []
        min_buy = buying_price + 1 if buying_price is not None else 1
        max_sell = selling_price if selling_price is not None else int(card_util) + 8
        for i in range(min_buy, min_buy + 8):
            for j in range(max(max_sell - 8, i + 1), max_sell):
                actions.append((i, j))
        return np.array(actions, dtype=('int,int'))