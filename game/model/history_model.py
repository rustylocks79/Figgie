from game.figgie import Suit, Figgie
from game.model.utility_model import PriceModel


class HistoryModel(PriceModel):
    def get_expected_utility(self, suit: Suit, figgie: Figgie):
        return 1