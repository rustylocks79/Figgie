from math import sqrt
from random import randint

import numpy as np

from api.cfr import CFRMinimizer
from api.game import *
from api.one_action_agent import OneActionAgent
from api.strategy_agent import StrategyAgent


def isg_basic(kuhn) -> str:
    return str(kuhn.cards[kuhn.get_active_player()]) + kuhn.history

def ag_basic(kuhn) -> np.ndarray:
    return np.array([0, 1], dtype=int)

class KuhnPoker(Game):
    def __init__(self):
        self.cards = [0, 0]
        self.history = ''
        self.deal()
        self.active_player = 0

    def reset(self) -> None:
        self.deal()
        self.history = ''
        self.active_player = 0

    def deal(self) -> None:
        self.cards[0] = randint(0, 2)
        self.cards[1] = randint(0, 2)
        while self.cards[0] == self.cards[1]:
            self.cards[1] = randint(0, 2)

    def get_active_player(self) -> int:
        return self.active_player

    def preform(self, action: int) -> None:
        self.history += 'p' if action == 0 else 'b'
        self.active_player += 1
        self.active_player %= 2

    def is_finished(self) -> bool:
        plays = len(self.history)
        if plays > 1:
            terminal_pass = self.history[plays - 1] == 'p'
            double_bet = self.history[plays - 2:plays] == 'bb'
            return terminal_pass or double_bet
        return False

    def get_utility(self) -> list:
        plays = len(self.history)
        terminal_pass = self.history[plays - 1] == 'p'
        double_bet = self.history[plays - 2:plays] == 'bb'
        is_player_card_higher = self.cards[0] > self.cards[1]
        if terminal_pass:
            if self.history == 'pp':
                utility = [1, -1] if is_player_card_higher else [-1, 1]
            else:
                utility = [1, -1]
            return utility
        elif double_bet:
            return [2, -2] if is_player_card_higher else [-2, 2]
        else:
            raise ValueError("game is not in terminal state. ")


if __name__ == '__main__':
    TOTAL_TRIALS = 100000
    game = KuhnPoker()
    minimizer = CFRMinimizer(game, isg_basic, ag_basic)
    minimizer.train(TOTAL_TRIALS)
    strategy = minimizer.get_strategy()

    print('Player 2 always passes')
    agent1 = StrategyAgent(strategy, isg_basic, ag_basic)
    agent2 = OneActionAgent(0)  # 0 is pass
    game.reset()
    game.play([agent1, agent2], 10_000)

    print('Player 2 always bets')
    agent2 = OneActionAgent(1)  # 1 is bet
    game.reset()
    game.play([agent1, agent2], 10_000)

    print('Player 2 uses cfr')
    agent2 = StrategyAgent(strategy, isg_basic, ag_basic)
    game.reset()
    game.play([agent1, agent2], 10_000)

    alpha = 1.0 / 3 * strategy['0'][0] + 1.0 / 9 * strategy['2'][0] + 1.0 / 3 * (strategy['1pb'][0] - 1.0 / 3)
    square_error = 0.0
    keys = ["0", "0b", "0p", "0pb", "1", "1b", "1p", "1pb", "2", "2b", "2p", "2pb"]
    targets = [alpha, 0.0, 1.0 / 3, 0.0, 0.0, 1.0 / 3, 0.0, alpha + 1.0 / 3, 3 * alpha, 1.0, 1.0, 1.0]
    for i in range(len(keys)):
        err = targets[i] - strategy[keys[i]][0]
        square_error += err * err

    print("Results: RMSE over optimal strategy: {:.6f}".format(sqrt(square_error / TOTAL_TRIALS)))
    print("Betting probabilities")
    print("Key\tAveStrategy\tOptimal")
    for i in range(len(keys)):
        print("{}\t{:.4f}\t{:.4f}".format(keys[i], strategy[keys[i]][0], targets[i]))
