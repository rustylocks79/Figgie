from math import ceil, floor

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.figgie import Figgie, Suit
from game.model.utility_model import UtilityModel


class BasicAgent(Agent):
    def __init__(self, index: int, model: UtilityModel):
        super().__init__(index)
        self.util_model = model

    def get_action(self, figgie: Figgie) -> Action:
        market = figgie.markets[Suit.CLUBS.value]

        buy_exp_util = self.util_model.get_expected_utility_change(figgie, self.index,
                                                                   BuyAction(self.index, '', Suit.CLUBS))
        sell_exp_util = self.util_model.get_expected_utility_change(figgie, self.index,
                                                                    SellAction(self.index, '', Suit.CLUBS))

        if market.can_buy(self.index)[0]:
            if buy_exp_util > market.selling_price:
                return BuyAction(self.index, '', Suit.CLUBS)
        elif market.can_sell(self.index)[0]:
            if abs(sell_exp_util) < market.buying_price:
                return SellAction(self.index, '', Suit.CLUBS)

        buying_price = max(floor(buy_exp_util) - 1, 1)
        selling_price = max(abs(ceil(sell_exp_util)) + 1, 1)

        will_buy = market.can_bid(self.index, buying_price)[0]
        will_sell = market.can_ask(self.index, selling_price)[0]

        if will_buy and will_sell:
            if buying_price >= selling_price:  # TODO: this is a temp fix
                return BidAction(self.index, '', Suit.CLUBS, buying_price)
            return AtAction(self.index, '', Suit.CLUBS, buying_price, selling_price)
        elif will_buy:
            return BidAction(self.index, '', Suit.CLUBS, buying_price)
        elif will_sell:
            return AskAction(self.index, '', Suit.CLUBS, selling_price)
        else:
            return PassAction(self.index, '')
