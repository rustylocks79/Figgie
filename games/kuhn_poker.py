from random import *
from games.game import *


class KuhnPoker(Game):
    def __init__(self):
        self.cards = [0, 0]
        self.history = ''
        self.draw()
        self.current_player = 0

    def get_actions(self) -> list:
        return ['p', 'b']

    def is_finished(self) -> bool:
        plays = len(self.history)
        if plays > 1:
            terminal_pass = self.history[plays - 1] == 'p'
            double_bet = self.history[plays - 2:plays] == 'bb'
            return terminal_pass or double_bet
        return False

    def get_current_info_set(self) -> str:
        return str(self.cards[self.get_current_player()]) + self.history

    def get_utility(self, player_index: int) -> int:
        plays = len(self.history)
        opponent = 1 - player_index
        terminal_pass = self.history[plays - 1] == 'p'
        double_bet = self.history[plays - 2:plays] == 'bb'
        is_player_card_higher = self.cards[player_index] > self.cards[opponent]
        if terminal_pass:
            if self.history == 'pp':
                utility = 1 if is_player_card_higher else -1
            else:
                utility = 1
            return utility
        elif double_bet:
            return 2 if is_player_card_higher else -2
        else:
            raise  # TODO

    def get_current_player(self):
        return self.current_player

    def preform(self, action: str):
        self.history += action
        self.current_player += 1
        self.current_player %= 2

    def draw(self):
        self.cards[0] = randint(0, 2)
        self.cards[1] = randint(0, 2)
        while self.cards[0] == self.cards[1]:
            self.cards[1] = randint(0, 2)

    def reset(self) -> None:
        self.draw()
        self.history = ''
        self.current_player = 0
