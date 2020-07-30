from game.agent.agent import Agent
from game.figgie import Figgie, Suit
from game.model.price_model import PriceModel


class BasicAgent(Agent):
    def __init__(self, index: int, model: PriceModel):
        super().__init__(index)
        self.priceModel = model

    def get_action(self, figgie: Figgie) -> tuple:
        expected_util = self.priceModel.get_expected_utility(Suit.CLUBS, figgie)
        market = figgie.markets[Suit.CLUBS.value]
        hand = figgie.cards[self.index]
        if market.can_buy(self.index)[0] and market.selling_price < expected_util:
            return 'buy', Suit.CLUBS
        elif market.can_sell(self.index)[0] and market.buying_price > expected_util:
            return 'sell', Suit.CLUBS

        if market.buying_price is None:
            return 'bid', Suit.CLUBS, round(expected_util) - 1
        else:
            return 'bid', Suit.CLUBS, market.buying_price + 1

        if market.selling_price is None and hand[Suit.CLUBS.value] >= 1:
            return 'ask', Suit.CLUBS, round(expected_util + 1)
        else:
            return 'ask', Suit.CLUBS, market.selling_price - 1

        return ('pass', )
