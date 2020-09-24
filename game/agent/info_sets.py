from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.agent.regret_agent import *


def get_last_transaction(figgie: Figgie, operation: str, suit: Suit) -> str:
    if operation == 'ask':
        last_sell = figgie.markets[suit.value].last_price_sold
        return str(last_sell) if last_sell is not None else 'N'
    elif operation == 'bid':
        last_buy = figgie.markets[suit.value].last_price_bought
        return str(last_buy) if last_buy is not None else 'N'
    elif operation == 'at':
        last_buy = figgie.markets[suit.value].last_price_bought
        last_sell = figgie.markets[suit.value].last_price_sold
        return str(last_buy) if last_buy is not None else 'N' + ',' + str(last_sell) if last_sell is not None else 'N'
    else:
        raise ValueError('Invalid Operation: ' + operation)


class StandardGenerator(InfoSetGenerator):
    def __init__(self, name):
        super().__init__(name)

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
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

    def generate_bid_actions(self, card_util: float, buying_price: int, target_suit: Suit) -> list:
        actions = []
        min_buy = buying_price + 1 if buying_price is not None else 1
        for i in range(min_buy, min_buy + 8):
            actions.append(BidAction(target_suit, i))
        return actions

    def generate_ask_actions(self, card_util: float, selling_price: int, target_suit: Suit) -> list:
        actions = []
        max_sell = selling_price if selling_price is not None else int(card_util) + 8
        for i in range(max(max_sell - 8, 1), max_sell):
            actions.append(AskAction(target_suit, i))
        return actions

    def generate_at_actions(self, card_util: float, buying_price: int, selling_price: int, target_suit: Suit):
        actions = []
        min_buy = buying_price + 1 if buying_price is not None else 1
        max_sell = selling_price if selling_price is not None else int(card_util) + 8
        for i in range(min_buy, min_buy + 8):
            for j in range(max(max_sell - 8, i + 1), max_sell):
                actions.append(AtAction(target_suit, i, j))
        return actions


class InfoSetH(StandardGenerator):
    def __init__(self):
        super().__init__('h')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        hand = str(figgie.cards[figgie.active_player])
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + hand[target_suit.value]


class InfoSetT(StandardGenerator):
    def __init__(self):
        super().__init__('t')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + str(market.transactions)


class InfoSetL(StandardGenerator):
    def __init__(self):
        super().__init__('l')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        last_transaction = get_last_transaction(figgie, target_operation, target_suit)
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + last_transaction


class InfoSetHT(StandardGenerator):
    def __init__(self):
        super().__init__('ht')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        hand = str(figgie.cards[figgie.active_player])
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + hand[target_suit.value] + ',' + str(market.transactions)


class InfoSetHL(StandardGenerator):
    def __init__(self):
        super().__init__('hl')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        hand = str(figgie.cards[figgie.active_player])
        last_transaction = get_last_transaction(figgie, target_operation, target_suit)
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + hand + ',' + last_transaction


class InfoSetTL(StandardGenerator):
    def __init__(self):
        super().__init__('tl')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        last_transaction = get_last_transaction(figgie, target_operation, target_suit)
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + str(market.transactions) + ',' + last_transaction


class InfoSetHTL(StandardGenerator):
    def __init__(self):
        super().__init__('htl')

    def generate_info_set(self, figgie: Figgie, card_util: float, target_operation: str, target_suit: Suit):
        market = figgie.markets[target_suit.value]
        hand = str(figgie.cards[figgie.active_player])
        last_transaction = get_last_transaction(figgie, target_operation, target_suit)
        return super().generate_info_set(figgie, card_util, target_operation, target_suit) + ',' + hand + ',' + str(market.transactions) + ',' + last_transaction