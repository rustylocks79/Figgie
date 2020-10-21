from figgie import Suit, Figgie, Action


class UtilityModel:
    def __init__(self, name):
        self.name = name

    def get_card_utility(self, figgie: Figgie, index: int, suit: Suit) -> float:
        pass

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        pass

    def reset(self):
        pass

