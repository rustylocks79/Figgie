from game.agent.regret_agent import *
from game.figgie import Figgie


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

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        market = figgie.markets[suit.value]
        if action == 'bid':
            return 'bid,{},{}'.format(util, market.buying_price if market.has_buyer() else 'N')
        elif action == 'ask':
            return 'ask,{},{}'.format(util, market.selling_price if market.has_seller() else 'N')
        elif action == 'at':
            return 'at,{},{},{}'.format(util, market.buying_price if market.has_buyer() else 'N',
                                        market.selling_price if market.has_seller() else 'N')
        else:
            raise ValueError("Invalid action: {}".format(action))


class InfoSetH(StandardGenerator):
    def __init__(self):
        super().__init__('h')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        hand = str(figgie.cards[figgie.active_player])
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + hand[suit.value]


class InfoSetT(StandardGenerator):
    def __init__(self):
        super().__init__('t')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        transactions = str(agent.transactions[suit.value])
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + transactions


class InfoSetL(StandardGenerator):
    def __init__(self):
        super().__init__('l')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        last_transaction = get_last_transaction(figgie, action, suit)
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + last_transaction


class InfoSetHT(StandardGenerator):
    def __init__(self):
        super().__init__('ht')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        hand = str(figgie.cards[figgie.active_player])
        transactions = str(agent.transactions[suit.value])
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + hand[suit.value] + ',' + transactions


class InfoSetHL(StandardGenerator):
    def __init__(self):
        super().__init__('hl')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        hand = str(figgie.cards[figgie.active_player])
        last_transaction = get_last_transaction(figgie, action, suit)
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + hand + ',' + last_transaction


class InfoSetTL(StandardGenerator):
    def __init__(self):
        super().__init__('tl')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        transactions = str(agent.transactions[suit.value])
        last_transaction = get_last_transaction(figgie, action, suit)
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + transactions + ',' + last_transaction


class InfoSetHTL(StandardGenerator):
    def __init__(self):
        super().__init__('htl')

    def generate_info_set(self, action: str, suit: Suit, figgie: Figgie, agent: Agent, util: float):
        hand = str(figgie.cards[figgie.active_player])
        transactions = str(agent.transactions[suit.value])
        last_transaction = get_last_transaction(figgie, action, suit)
        return super().generate_info_set(action, suit, figgie, agent, util) + ',' + hand + ',' + transactions + ',' + last_transaction