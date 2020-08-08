from random import choice, randint, shuffle

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.figgie import Figgie, SUITS, Suit

MAX_PRICE = 30  # TODO: come up with formula


class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def get_action(self, figgie: Figgie) -> Action:
        player = figgie.active_player
        operations = []
        suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
        shuffle(suits)
        action_suit = None
        for suit in suits:
            market = figgie.markets[suit.value]
            hand = figgie.cards[player]
            if (market.selling_price is None or market.selling_price > 1) and hand[suit.value] >= 1:
                operations.append('ask')
            if market.buying_price is None or market.buying_price < MAX_PRICE:
                operations.append('bid')
            if market.can_buy(player)[0]:
                operations.append('buy')
            if market.can_sell(player)[0]:
                operations.append('sell')
            if len(operations) > 0:
                action_suit = suit
                break
        if len(operations) == 0:
            return PassAction()
        operation = choice(operations)
        market = figgie.markets[action_suit.value]
        if operation == 'ask':
            return AskAction(action_suit, randint(1, market.selling_price - 1 if market.selling_price is not None else MAX_PRICE))
        elif operation == 'bid':
            return BidAction(action_suit, randint(market.buying_price + 1 if market.buying_price is not None else 1, MAX_PRICE))
        elif operation == 'buy':
            return BuyAction(action_suit)
        elif operation == 'sell':
            return SellAction(action_suit)
        elif operation == 'at':
            buying_price = randint(market.buying_price + 1 if market.buying_price is not None else 1, MAX_PRICE)
            selling_price = randint(1, market.selling_price - 1 if market.selling_price is not None else MAX_PRICE)
            return AtAction(action_suit, buying_price, selling_price)
