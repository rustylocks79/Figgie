from queue import Queue
from random import choice, randint, shuffle
from enum import Enum
import numpy as np

NUM_PLAYERS = 4
NUM_ROUNDS = 8
STARTING_CHIPS = 250


class Suit(Enum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def opposite(self):
        if self == Suit.CLUBS:
            return Suit.SPADES
        elif self == Suit.DIAMONDS:
            return Suit.HEARTS
        elif self == Suit.HEARTS:
            return Suit.DIAMONDS
        elif self == Suit.SPADES:
            return Suit.CLUBS

    def __str__(self):
        if self == Suit.CLUBS:
            return 'clubs'
        elif self == Suit.DIAMONDS:
            return 'diamonds'
        elif self == Suit.HEARTS:
            return 'hearts'
        elif self == Suit.SPADES:
            return 'spades'

    def to_abbr(self) -> str:
        if self == Suit.CLUBS:
            return 'C'
        elif self == Suit.DIAMONDS:
            return 'D'
        elif self == Suit.HEARTS:
            return 'H'
        elif self == Suit.SPADES:
            return 'S'

    @staticmethod
    def from_abbr(value: str):
        if value == 'C':
            return Suit.CLUBS
        elif value == 'D':
            return Suit.DIAMONDS
        elif value == 'H':
            return Suit.HEARTS
        elif value == 'S':
            return Suit.SPADES
        else:
            raise ValueError('Invalid suit abbr {}'.format(value))

    @staticmethod
    def from_value(value: int):
        if value == Suit.CLUBS.value:
            return Suit.CLUBS
        elif value == Suit.DIAMONDS.value:
            return Suit.DIAMONDS
        elif value == Suit.HEARTS.value:
            return Suit.HEARTS
        elif value == Suit.SPADES.value:
            return Suit.SPADES
        else:
            raise ValueError('Invalid suit value {}'.format(value))


SUITS = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]


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
        self.active_player = 0
        self.queue = Queue(4)
        self.__new_queue()
        self.round = 0

    def reset(self) -> None:
        """
        Resets the game to a start state.
        """
        self.deal()
        self.chips = np.full(NUM_PLAYERS, STARTING_CHIPS, dtype=int)
        self.clear_markets()
        self.active_player = 0
        self.__new_queue()
        self.round = 0

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

    def get_active_player(self) -> int:
        """
        :return: the active player in the games current state.
        """
        return self.active_player

    def normalize_index(self, index) -> int:
        """
        :param index: the actual index
        :return: converts the index to an index assuming that the actual player is always player 0.
        """
        result = index - self.active_player
        if result < 0:
            result += 4
        return result

    def denormalize_index(self, index) -> int:
        """
        :param index: a normalized index
        :return: the denormalized index
        """
        return (index + self.active_player) % 4

    def preform(self, action: tuple) -> None:
        """
        :param action: the string action to be preformed
        :return: change the state of the game by preforming the provided action.
        """

        operation = action[0]
        if operation == 'ask':
            suit = action[1]
            price = action[2]
            self.markets[suit.value].ask(self.active_player, price)
        elif operation == 'bid':
            suit = action[1]
            price = action[2]
            self.markets[suit.value].bid(self.active_player, price)
        elif operation == 'buy':
            suit = action[1]
            self.markets[suit.value].buy(self.active_player)
            self.clear_markets()
        elif operation == 'sell':
            suit = action[1]
            self.markets[suit.value].sell(self.active_player)
            self.clear_markets()
        elif operation == 'at':
            suit = action[1]
            price1 = action[2]
            price2 = action[3]
            self.markets[suit.value].at(self.active_player, price1, price2)
        elif operation == 'pass':
            pass
        else:
            raise ValueError('Unknown operation: {}'.format(operation))

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
        for i in range(trials):
            while not self.is_finished():
                player = self.get_active_player()
                action = agents[player].get_action(self)
                if verbose:
                    print('agent {}: {}', player, action)
                self.preform(action)
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
        elif self.selling_price is not None and amount >= self.selling_price:
            return False, 'new amount is higher than current selling price {}. '.format(self.selling_price)
        return True, 'success'

    def ask(self, player: int, amount: int) -> None:
        can, reason = self.can_ask(player, amount)
        if not can:
            raise ValueError('player {} can not ask {} for {} because {}'.format(player, amount, self.suit.name, reason))
        self.selling_price = amount
        self.selling_player = player

    def can_bid(self, player: int, amount: int) -> tuple:
        chips = self.figgie.chips[player]
        if amount <= 0:
            return False, 'amount must be greater than 0'
        if chips < amount:
            return False, 'player only has {} chips'.format(chips)
        if self.buying_price is not None and amount <= self.buying_price:
            return False, 'new amount is lower than current buying price {}'.format(self.buying_price)
        return True, 'success'

    def bid(self, player: int, amount: int) -> None:
        can, reason = self.can_bid(player, amount)
        if not can:
            raise ValueError('player {} can not bid {} for {} because {}. '.format(player, amount, self.suit.name, reason))
        self.buying_price = amount
        self.buying_player = player

    def at(self, buying_price: int, selling_price: int, player: int) -> None:
        if buying_price >= selling_price:
            raise ValueError('player {} can not {} at {} because buying price must be less than selling price. '
                             .format(player, buying_price, selling_price))
        self.bid(buying_price, player)
        self.ask(selling_price, player)

    def can_buy(self, player: int) -> tuple:
        chips = self.figgie.chips[player]
        if player == self.selling_player:
            return False, 'cannot buy from yourself'
        if self.selling_price is None:
            return False, 'no one has set an selling price'
        if chips < self.selling_price:
            return False, 'player only has {} chips'.format(chips)
        if self.figgie.cards[self.selling_player][self.suit.value] < 1:
            return False, 'selling player does not have the card'
        return True, 'success'

    def buy(self, player: int) -> None:
        can, reason = self.can_buy(player)
        if not can:
            raise ValueError("Player {} can buy {} from {} because {}".format(player, self.suit.name, self.selling_player, reason))

        self.figgie.chips[self.selling_player] += self.selling_price
        self.figgie.cards[self.selling_player][self.suit.value] -= 1

        self.figgie.chips[player] -= self.selling_price
        self.figgie.cards[player][self.suit.value] += 1

    def can_sell(self, player: int) -> tuple:
        if player is self.buying_player:
            return False, 'cannot sell to yourself'
        if self.buying_price is None:
            return False, 'no one has set a buying price'
        if self.figgie.chips[self.buying_player] < self.buying_price:
            return False, 'buying player only has {} chips'.format(self.figgie.chips[self.buying_player])
        if self.figgie.cards[player][self.suit.value] < 1:
            return False, 'player does not have the card to sell'
        return True, 'success'

    def sell(self, player: int):
        can, reason = self.can_sell(player)
        if not can:
            raise ValueError('player {} can not sell {} to player {} because {}'.format(player, self.suit.name, self.buying_player, reason))

        self.figgie.chips[player] += self.buying_price
        self.figgie.cards[player][self.suit.value] -= 1

        self.figgie.chips[self.buying_player] -= self.buying_price
        self.figgie.cards[self.buying_player][self.suit.value] += 1

    def clear(self):
        self.buying_price = None
        self.buying_player = None
        self.selling_price = None
        self.selling_player = None
