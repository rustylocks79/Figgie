import numpy as np

from figgie import Figgie, Action


class UtilityModel:
    def __init__(self, name):
        self.name = name

    def get_card_utility(self, figgie: Figgie, index: int) -> np.ndarray:
        pass

    def on_action(self, figgie: Figgie, index: int, action: Action) -> None:
        pass

    def reset(self):
        pass

