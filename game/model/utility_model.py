from game.action.action import Action
from game.figgie import Suit, Figgie


class UtilityModel:
    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        pass

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        pass

    def reset(self):
        pass

