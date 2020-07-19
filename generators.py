from random import randint

import numpy as np

from figgie import SUITS, from_value, ASK, BID, BUY, SELL


def isg_basic(figgie) -> str:
    #  TODO: this does not account for chips
    result = ''
    hand = figgie.cards[figgie.get_active_player()]
    for suit in SUITS:
        result += suit.to_abbr() + str(hand[suit.value])
    result += ':'
    for market in figgie.markets:
        result += market.suit.to_abbr()
        result += str(figgie.normalize_index(market.buying_player)) + str(
            market.buying_price) if market.buying_price is not None else 'NN'
        result += str(figgie.normalize_index(market.selling_player)) + str(
            market.selling_price) if market.selling_price is not None else 'NN'
    return result


def isg_abstract(figgie):
    result = ''
    hand = figgie.cards[figgie.get_active_player()]
    me = figgie.get_active_player()
    for suit in SUITS:
        result += suit.to_abbr() + str(hand[suit.value])
    result += ':'
    for market in figgie.markets:
        result += market.suit.to_abbr()

        #buying
        if market.buying_player == me:
            result += 'M'  # ME
        else:
            result += 'O'  # Other
        if market.buying_price is None:
            result += 'N'  # None
        elif market.buying_price == 9:
            result += '9'  # can't out bid
        else:
            result += 'B'  # can buy

        # selling
        if market.selling_player == me:
            result += 'M'  # ME
        else:
            result += 'O'  # Other
        if market.selling_price is None:
            result += 'N'  # None
        elif market.selling_price == 1:
            result += '1'  # can't out ask
        else:
            result += 'S'  # can sell
    return result


def ag_basic(figgie) -> np.ndarray:
    hand = figgie.cards[figgie.active_player]
    result = []
    for suit in SUITS:
        market = figgie.markets[suit.value]
        suit_code = suit.value * 10
        # asking
        if hand[suit.value] >= 1:
            ask_code = ASK * 100
            if market.selling_price is not None:
                for i in range(1, market.selling_price):
                    result.append(ask_code + suit_code + i)
            else:
                for i in range(1, 10):
                    result.append(ask_code + suit_code + i)

        # bidding
        bid_code = BID * 100
        if market.buying_price is not None:
            for i in range(market.buying_price + 1, 10):
                result.append(bid_code + suit_code + i)
        else:
            for i in range(1, 10):
                result.append(bid_code + suit_code + i)

        # buying
        buy_code = BUY * 100
        if market.selling_price is not None and market.selling_player != figgie.active_player:
            result.append(buy_code + suit_code)

        # selling
        sell_code = SELL * 100
        if (market.buying_price is not None and market.buying_player != figgie.active_player) and hand[suit.value] >= 1:
            result.append(sell_code + suit_code)
    return np.array(result, dtype=int)


def ag_abstract(figgie) -> np.ndarray:
    hand = figgie.cards[figgie.active_player]
    result = []
    for suit in SUITS:
        market = figgie.markets[suit.value]
        suit_code = suit.value * 10
        # asking
        if market.selling_price != 1 and hand[suit.value] >= 1:
            result.append(ASK * 100 + suit_code)

        # bidding
        if market.buying_price != 9:
            result.append((BID * 100) + suit_code)

        # buying
        if market.selling_price is not None and market.selling_player != figgie.active_player:
            result.append((BUY * 100) + suit_code)

        # selling
        if (market.buying_price is not None and market.buying_player != figgie.active_player) and hand[suit.value] >= 1:
            result.append((SELL * 100) + suit_code)
    return np.array(result, dtype=int)


def am_abstract(figgie, action: int) -> int:
    initial_action = action
    op = action // 100
    action %= 100
    suit = from_value(action // 10)
    if op == ASK:
        selling_price = figgie.markets[suit.value].selling_price
        return initial_action + randint(1, selling_price - 1 if selling_price is not None else 9)
    elif op == BID:
        buying_price = figgie.markets[suit.value].buying_price
        return initial_action + randint(buying_price + 1 if buying_price is not None else 1, 9)
    elif op == BUY or op == SELL:
        return initial_action
    else:
        raise ValueError('invalid initial action giving to mapping')