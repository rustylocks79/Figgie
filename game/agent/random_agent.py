from random import choice, randint, shuffle

from game.agent.agent import Agent
from game.figgie import Figgie, SUITS, Suit

MAX_PRICE = 30  # TODO: come up with formula


class RandomAgent(Agent):
    def __init__(self, index: int):
        super().__init__(index)

    def get_action(self, figgie: Figgie) -> tuple:
        operations = []
        suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
        shuffle(suits)
        for suit in suits:
            market = figgie.markets[suit.value]
            hand = figgie.cards[self.index]
            if (market.selling_price is None or market.selling_price > 1) and hand[suit.value] >= 1:
                operations.append('ask')
            if market.buying_price is None or market.buying_price < MAX_PRICE:
                operations.append('bid')
            if market.can_buy(self.index)[0]:
                operations.append('buy')
            if market.can_sell(self.index)[0]:
                operations.append('sell')
            if len(operations) > 0:
                break
        if len(operations) == 0:
            raise ValueError('No possible moves. ')
        operation = choice(operations)
        if operation == 'ask':
            action = (operation, suit, randint(1, market.selling_price - 1 if market.selling_price is not None else MAX_PRICE))
        elif operation == 'bid':
            action = (operation, suit, randint(market.buying_price + 1 if market.buying_price is not None else 1, MAX_PRICE))
        else:
            action = (operation, suit)
        return action
