from math import ceil, floor

from game.action.action import Action
from game.action.ask_action import AskAction
from game.action.at_action import AtAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.agent.agent import Agent
from game.figgie import Figgie, Suit, Market
from game.model.utility_model import UtilityModel


class BasicAgent(Agent):
    def __init__(self, model: UtilityModel):
        super().__init__()
        self.util_model = model

    def get_action(self, figgie: Figgie) -> Action:
        player = figgie.active_player
        market = figgie.markets[Suit.CLUBS.value]

        card_util = round(self.util_model.get_card_utility(figgie, player, Suit.CLUBS))
        actual_util = round(self.cheating_model.get_card_utility(figgie, player, Suit.CLUBS))
        self.add_prediction(card_util, actual_util)

        if market.can_buy(player)[0]:
            # if the utility gained by buying the card is greater than the cost of the card.
            if card_util > market.selling_price:
                return BuyAction(Suit.CLUBS)
        elif market.can_sell(player)[0]:
            # if the utility lost by selling the card is less than the value received for selling the card.
            if card_util < market.buying_price:
                return SellAction(Suit.CLUBS)

        will_bid = False
        will_ask = False
        buying_price = 0
        selling_price = 0

        # if the expected utility for buying the card is buying price (Can offer a bigger buy).
        if not market.is_buyer() or card_util > market.buying_price + 1 and card_util != 0:
            buying_price = self.get_buying_price(figgie, card_util)
            will_bid = market.can_bid(player, buying_price)[0]

        # if the expected utility lost for selling the card is less than the selling price (Can offer a lower sell)
        if not market.is_seller() or card_util < market.selling_price - 1:
            selling_price = self.get_selling_price(figgie, card_util)
            will_ask = market.can_ask(player, selling_price)[0]

        will_at = will_bid and will_ask and buying_price < selling_price

        if will_at:
            return AtAction(Suit.CLUBS, buying_price, selling_price)
        elif will_bid:
            return BidAction(Suit.CLUBS, buying_price)
        elif will_at:
            return AskAction(Suit.CLUBS, selling_price)
        else:
            return PassAction()

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        self.util_model.on_action(figgie, index, action)

    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        pass

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        pass


class PlusOneAgent(BasicAgent):
    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        return max(card_util - 1, 1)

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        return max(card_util + 1, 1)


class MinusOneAgent(BasicAgent):
    def get_buying_price(self, figgie: Figgie, card_util: int) -> int:
        market = figgie.markets[Suit.CLUBS.value]
        if market.is_buyer():
            return market.buying_price + 1
        else:
            return max(card_util - 1, 1)

    def get_selling_price(self, figgie: Figgie, card_util: int) -> int:
        market = figgie.markets[Suit.CLUBS.value]
        if market.is_seller():
            return market.selling_price - 1
        else:
            return max(card_util + 1, 1)
