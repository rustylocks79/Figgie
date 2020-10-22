import numpy as np
import torch

from agent.models.utility_model import UtilityModel
from figgie import Figgie, SUITS
from train_model import Net


class AnnModel(UtilityModel):
    def __init__(self):
        super().__init__('ann')
        self.pot_rewards = {
            11: 1000,           # conceptually this makes no sense but making this so high ensure the model will not encourage the agent to sell goal cards.
            10: 10 * 10 + 100,  # [cards] * 10 + [10 pot]
            9: 9 * 10 + 100,    # [cards] * 10 + [10 pot]
            8: 8 * 10 + .33 * 120 + .67 * 100,   # [cards] * 10 + [prob. 8 goal] * [8 pot] + [prob. 10 goal] * [10 pot]
            7: 7 * 10 + .33 * 120 + .67 * 100,  # [cards] * 10 + [prob. 8 goal] * [8 pot] + [prob. 10 goal] * [10 pot]
            6: 6 * 10 + .33 * 120 + .67 * 100,  # [cards] * 10 + [prob. 8 goal] * [8 pot] + [prob. 10 goal] * [10 pot]

            # [other hands 10] = C(n+r-1,r-1)) where n = 5 and r = 3 so [other hands 10] = 21
            # [cards] * 10 + [prob 8 goal] * [8 pot] + [prob 10 goal] * (3/[other hands 10] * [10 pot]/2 + ([other hands 10] - 3)/[other hands 10] * [10 pot]])
            5: 5 * 10 + .33 * 120 + .67 * (3/21 * 100/2 + 18/21 * 100),

            # [other hands 10] = C(n+r-1,r-1)) where n = 6 and r = 3 so [other hands 10] = 28
            # [other hands 8] = C(n+r-1,r-1)) where n = 4 and r = 3 so [other hands 8] = 15
            # [cards] * 10 + [prob 8 goal] * (3/[other hands 8] * [8 pot] / 2 + ([other hands 8] - 3)/[other hands 8]) + [prob 10 goal] * (3/[other hands] * [10 pot]/2 * ([other hands 10] - 6)/[other hands 10] * [10 pot])
            4: 4 * 10 + .33 * (3/15 * 120/2 + 12/15 * 120) + .67 * (3/28 * 100/2 + 22/28 * 100),

            # [other hands 10] = C(n+r-1,r-1)) where n = 7 and r = 3 so [other hands 10] = 36
            # [other hands 8] = C(n+r-1,r-1)) where n = 5 and r = 3 so [other hands 8] = 21
            # [cards] * 10 + [prob 8 goal] * (3/[other hands 8] * [8 pot] / 3) + [prob 10 goal] * (3/[other hands 10] * [10 pot] / 2)
            3: 3 * 10 + .33 * (3/21 * 120/3) + .67 * (3/36 * 100 / 2),

            # [other hands 8] = C(n+r-1,r-1)) where n = 6 and r = 3 so [other hands 8] = 28
            # [cards] * 10 + [prob 8 goal] * (1/[other hands 8] * [8 pot] / 4)
            2: 2 * 10 + .33 * (1/28 * 120/4),

            1: 10,     # 1 * 10
            0: 0,      # 0 * 10
        }
        self.model = Net()
        self.model.load_state_dict(torch.load('ann/my_model.pt'))
        self.model.eval()

    def get_card_utility(self, figgie: Figgie, index: int) -> np.ndarray:
        hand = figgie.cards[index]
        result = np.full(4, 0, dtype=float)
        for s in SUITS:
            if hand[s.value] > 10:
                goal_suit = s.opposite()
                result[goal_suit.value] = (self.pot_rewards[hand[goal_suit.value] + 1] - self.pot_rewards[hand[goal_suit.value]])
                return result
        for s in SUITS:
            result[s.value] = (self.pot_rewards[hand[s.value] + 1] - self.pot_rewards[hand[s.value]])

        input = np.array([
            [cards for cards in figgie.cards[figgie.active_player]],
            [market.buying_price if market.buying_price is not None else 0 for market in figgie.markets],
            [market.selling_price if market.selling_price is not None else 0 for market in figgie.markets],
            [market.last_price if market.last_price is not None else 0 for market in figgie.markets],
            [market.operations for market in figgie.markets],
            [market.transactions for market in figgie.markets],
        ], dtype=np.float32).flatten()

        input = torch.from_numpy(input).view(-1, 24)
        percents = self.model(input)
        percents = torch.exp(percents)
        percents = percents.detach().numpy().flatten()
        return percents * result
