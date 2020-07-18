from figgie import SUITS, Figgie


def generate_info_set_basic(figgie: Figgie):
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


def generate_info_set_advanced(figgie):
    pass