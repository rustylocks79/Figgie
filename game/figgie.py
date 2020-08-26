from queue import Queue
from random import choice, randint, shuffle

import numpy as np

from game.suit import Suit, SUITS

NUM_PLAYERS = 4
NUM_ROUNDS = 16
STARTING_CHIPS = 250


class Figgie:
    def __init__(self):
        self.cards = []
        self.deal()
        self.chips = np.full(NUM_PLAYERS, STARTING_CHIPS, dtype=int)
        self.goal_suit = Suit.HEARTS
        self.markets = np.array([Market(Suit.CLUBS, self),
                                 Market(Suit.DIAMONDS, self),
                                 Market(Suit.HEARTS, self),
                                 Market(Suit.SPADES, self)], dtype=Market)
        self.queue = Queue(4)
        self.__new_queue()
        self.active_player = self.queue.get()
        self.round = 0
        self.history = []

    def reset(self) -> None:
        """
        Resets the game to a start state.
        """
        self.deal()
        self.chips = np.full(NUM_PLAYERS, STARTING_CHIPS, dtype=int)
        self.clear_markets()
        self.__new_queue()
        self.active_player = self.queue.get()
        self.round = 0
        self.history.clear()

    def clear_markets(self) -> None:
        """
        Resets all markets.
        """
        for market in self.markets:
            market.clear()

    def deal(self) -> None:
        """
        Deal a set of 40 cards evenly to all players
        """
        self.cards = np.zeros((4, 4), dtype=int)
        goal = randint(0, 3)
        self.goal_suit = SUITS[goal]
        schematic = [10, 10, 10, 10]
        schematic[self.goal_suit.opposite().value] = 12
        eight_suit = choice([i for i in range(4) if i != self.goal_suit.opposite().value])
        schematic[eight_suit] = 8
        deck = []

        for i in range(4):
            for j in range(schematic[i]):
                deck.append(SUITS[i])

        shuffle(deck)

        for i in range(NUM_PLAYERS):
            for j in range(10):
                suit = deck.pop()
                self.cards[i][suit.value] += 1

    def preform(self, action) -> None:
        """
        :param action: the string action to be preformed
        :return: change the state of the game by preforming the provided action.
        """
        action.index = self.active_player

        if action.operation == 'ask':
            self.markets[action.suit.value].ask(self.active_player, action.selling_price)
        elif action.operation == 'bid':
            self.markets[action.suit.value].bid(self.active_player, action.buying_price)
        elif action.operation == 'buy':
            action.seller = self.markets[action.suit.value].selling_player
            self.markets[action.suit.value].buy(self.active_player)
            self.clear_markets()
        elif action.operation == 'sell':
            action.buyer = self.markets[action.suit.value].buying_player
            self.markets[action.suit.value].sell(self.active_player)
            self.clear_markets()
        elif action.operation == 'at':
            self.markets[action.suit.value].at(self.active_player, action.buying_price, action.selling_price)
        elif action.operation == 'pass':
            pass
        else:
            raise ValueError('Unknown operation: {}'.format(action.operation))

        self.history.append(action)

        if self.queue.empty():
            self.__new_queue()
            self.round += 1
        self.active_player = self.queue.get()

    def is_finished(self) -> bool:
        """
        Returns True if the game is in a terminal state, False otherwise.
        """
        return self.round == NUM_ROUNDS

    def get_utility(self) -> np.ndarray:
        """
        Precondition: the game must be in a terminal state.
        Returns the utility achieved by all players.
        """
        utility = np.zeros(4)
        total_awarded = 0
        for i, hand in enumerate(self.cards):
            award = hand[self.goal_suit.value] * 10
            utility[i] = self.chips[i] + award
            total_awarded += award

        max_goal_cards = max(self.cards[i][self.goal_suit.value] for i in range(NUM_PLAYERS))
        winners = [j for j in range(NUM_PLAYERS) if self.cards[j][self.goal_suit.value] == max_goal_cards]

        prize = (200 - total_awarded) // len(winners)
        for winner in winners:
            utility[winner] += prize

        return utility

    def play(self, agents: list, trials: int, verbose=False):
        """
        Plays 'trials' number of games and records the results in the agent statistics
        :param agents: a list of agents (size must be 4)
        :param trials: the number of games to preform
        :param verbose: if true output each agent action to the console
        """
        for i in range(trials):
            while not self.is_finished():
                player = self.active_player
                action = agents[player].get_action(self)
                if verbose:
                    print(str(action))
                self.preform(action)
                for j, agent in enumerate(agents):
                    agent.on_action(self, j, action)
            utility = self.get_utility()
            for j, agent in enumerate(agents):
                agent.total_utility += utility[j]
            max_utility = max(utility)
            winners = [j for j in range(len(utility)) if utility[j] == max_utility]
            for winner in winners:
                agents[winner].wins += 1
            self.reset()

    def __new_queue(self):
        self.queue.queue.clear()
        random_order = [0, 1, 2, 3]
        shuffle(random_order)
        [self.queue.put(i) for i in random_order]


class Market:
    def __init__(self, suit: Suit, figgie: Figgie):
        self.buying_price = None
        self.buying_player = None
        self.selling_price = None
        self.selling_player = None
        self.suit = suit
        self.figgie = figgie

    def can_ask(self, player: int, amount: int) -> tuple:
        """
        :param player: the player to preform the ask
        :param amount: the amount of chips that the player is willing to pay for the card
        :return: a bool that is true if the ask can be preformed, false and a str stating the reason the ask can not be preformed if applicable
        """
        hand = self.figgie.cards[player]
        if amount <= 0:
            return False, 'amount must greater than 0'
        elif hand[self.suit.value] < 1:
            return False, 'player does not have the card to sell'
        elif self.is_seller() and amount >= self.selling_price:
            return False, 'new amount is higher than current selling price {}. '.format(self.selling_price)
        return True, 'success'

    def ask(self, player: int, amount: int) -> None:
        assert self.can_ask(player, amount)[0], 'player {} can not ask {} for {} because {}'.format(player, amount, self.suit.name, self.can_ask(player, amount)[1])
        self.selling_price = amount
        self.selling_player = player

    def can_bid(self, player: int, amount: int) -> tuple:
        chips = self.figgie.chips[player]
        if amount <= 0:
            return False, 'amount must be greater than 0'
        if chips < amount:
            return False, 'player only has {} chips'.format(chips)
        if self.is_buyer() and amount <= self.buying_price:
            return False, 'new amount is lower than current buying price {}'.format(self.buying_price)
        return True, 'success'

    def bid(self, player: int, amount: int) -> None:
        assert self.can_bid(player, amount)[0], 'player {} can not bid {} for {} because {}. '.format(player, amount, self.suit.name, self.can_bid(player, amount)[1])
        self.buying_price = amount
        self.buying_player = player

    def can_at(self, player: int, buying_price: int, selling_price: int) -> tuple:
        can, reason = self.can_bid(player, buying_price)
        if not can:
            return can, reason
        can, reason = self.can_ask(player, selling_price)
        if not can:
            return can, reason
        if buying_price >= selling_price:
            return False, 'buying price must be less than selling price.'
        return True, 'success'

    def at(self, player: int, buying_price: int, selling_price: int) -> None:
        assert self.can_at(player, buying_price, selling_price)[0], 'player {} can not {} at {} because {}'.format(player, buying_price, selling_price, self.can_at(player, buying_price, selling_price)[1])
        self.bid(player, buying_price)
        self.ask(player, selling_price)

    def can_buy(self, player: int) -> tuple:
        chips = self.figgie.chips[player]
        if player == self.selling_player:
            return False, 'cannot buy from yourself'
        if not self.is_seller():
            return False, 'no one has set an selling price'
        if chips < self.selling_price:
            return False, 'player only has {} chips'.format(chips)
        if self.figgie.cards[self.selling_player][self.suit.value] < 1:
            return False, 'selling player does not have the card'
        return True, 'success'

    def buy(self, player: int) -> None:
        assert self.can_buy(player), 'Player {} can buy {} from {} because {}'.format(player, self.suit.name, self.selling_player, self.can_buy(player)[1])

        self.figgie.chips[self.selling_player] += self.selling_price
        self.figgie.cards[self.selling_player][self.suit.value] -= 1

        self.figgie.chips[player] -= self.selling_price
        self.figgie.cards[player][self.suit.value] += 1

    def can_sell(self, player: int) -> tuple:
        if player is self.buying_player:
            return False, 'cannot sell to yourself'
        if not self.is_buyer():
            return False, 'no one has set a buying price'
        if self.figgie.chips[self.buying_player] < self.buying_price:
            return False, 'buying player only has {} chips'.format(self.figgie.chips[self.buying_player])
        if self.figgie.cards[player][self.suit.value] < 1:
            return False, 'player does not have the card to sell'
        return True, 'success'

    def sell(self, player: int):
        assert self.can_sell(player), 'player {} can not sell {} to player {} because {}'.format(player, self.suit.name, self.buying_player, self.can_sell(player)[1])

        self.figgie.chips[player] += self.buying_price
        self.figgie.cards[player][self.suit.value] -= 1

        self.figgie.chips[self.buying_player] -= self.buying_price
        self.figgie.cards[self.buying_player][self.suit.value] += 1

    def is_buyer(self) -> bool:
        return self.buying_price is not None

    def is_seller(self) -> bool:
        return self.selling_price is not None

    def clear(self):
        self.buying_price = None
        self.buying_player = None
        self.selling_price = None
        self.selling_player = None
