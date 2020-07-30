from game.agent.agent import Agent
from game.figgie import Figgie, Suit
from game.model.utility_model import UtilityModel


class BasicAgent(Agent):
    def __init__(self, index: int, model: UtilityModel):
        super().__init__(index)
        self.utilModel = model

    def get_action(self, figgie: Figgie) -> tuple:
        current_exp_util = self.utilModel.get_expected_utility(figgie, self.index)
        market = figgie.markets[Suit.CLUBS.value]
        hand = figgie.cards[self.index]
        if market.can_buy(self.index)[0]:
            buy_exp_util = self.utilModel.get_expected_utility(figgie, self.index, ('buy', Suit.CLUBS))
            if current_exp_util < buy_exp_util:
                return 'buy', Suit.CLUBS
        elif market.can_sell(self.index)[0]:
            sell_exp_util = self.utilModel.get_expected_utility(figgie, self.index, ('sell', Suit.CLUBS))
            if current_exp_util < sell_exp_util:
                return 'sell', Suit.CLUBS

        return ('pass',)

        if market.buying_price is None:
            return 'bid', Suit.CLUBS, round(expected_util) - 1
        else:
            return 'bid', Suit.CLUBS, market.buying_price + 1

        if market.selling_price is None and hand[Suit.CLUBS.value] >= 1:
            return 'ask', Suit.CLUBS, round(expected_util + 1)
        else:
            return 'ask', Suit.CLUBS, market.selling_price - 1

        return ('pass', )
