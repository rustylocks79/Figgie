from game.figgie import Suit, Figgie
from game.model.price_model import PriceModel


class SimpleModel(PriceModel):
    def get_expected_utility(self, suit: Suit, figgie: Figgie):
        return 0.75 * 0 + 0.25 * 10
