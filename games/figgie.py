from enum import Enum
from random import choice, randint, shuffle

import numpy as np

from api.game import Game

NUM_PLAYERS = 4
NUM_ROUNDS = 8
STARTING_CHIPS = 250

ASK = 0
BID = 1
BUY = 2
SELL = 3


class Suit(Enum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def opposite(self):
        if self.value == Suit.CLUBS.value:
            return Suit.SPADES
        elif self.value == Suit.DIAMONDS.value:
            return Suit.HEARTS
        elif self.value == Suit.HEARTS.value:
            return Suit.DIAMONDS
        elif self.value == Suit.SPADES.value:
            return Suit.CLUBS

    def to_abbr(self) -> str:
        if self == Suit.CLUBS:
            return 'C'
        elif self == Suit.DIAMONDS:
            return 'D'
        elif self == Suit.HEARTS:
            return 'H'
        elif self == Suit.SPADES:
            return 'S'


def from_value(value: int) -> Suit:
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


class Figgie(Game):
    def __init__(self):
        self.cards = []
        self.deal()
        self.chips = np.array([STARTING_CHIPS] * NUM_PLAYERS)
        self.goal_suit = Suit.HEARTS
        self.markets = np.array([Market(Suit.CLUBS, self),
                                 Market(Suit.DIAMONDS, self),
                                 Market(Suit.HEARTS, self),
                                 Market(Suit.SPADES, self)], dtype=Market)
        self.active_player = 0
        self.round = 0

    def reset(self) -> None:
        self.deal()
        self.chips = [STARTING_CHIPS] * NUM_PLAYERS
        self.clear_markets()
        self.active_player = 0
        self.round = 0

    def clear_markets(self):
        for market in self.markets:
            market.clear()

    def deal(self):
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

    def get_actions(self) -> np.ndarray:
        hand = self.cards[self.active_player]
        result = []
        for suit in SUITS:
            market = self.markets[suit.value]
            suit_code = suit.value * 10
            # asking
            if hand[suit.value] >= 1:
                ask_code = ASK * 100
                if market.selling_price is not None:
                    for i in range(1, market.selling_price):
                        result.append(ask_code + suit_code + i)
                else:
                    for i in range(1, 10):
                        result.append(ask_code + suit_code + i)

            # bidding
            bid_code = BID * 100
            if market.buying_price is not None:
                for i in range(market.buying_price + 1, 10):
                    result.append(bid_code + suit_code + i)
            else:
                for i in range(1, 10):
                    result.append(bid_code + suit_code + i)

            # buying
            buy_code = BUY * 100
            if market.selling_price is not None and market.selling_player != self.active_player:
                result.append(buy_code + suit_code)

            # selling
            sell_code = SELL * 100
            if (market.buying_price is not None and market.buying_player != self.active_player) and hand[
                suit.value] >= 1:
                result.append(sell_code + suit_code)
        return np.array(result, dtype=int)

    def get_action_text(self, action: int) -> str:
        op = action // 100
        action %= 100
        suit = from_value(action // 10)
        if op == ASK:
            return 'ask {} {}'.format(suit.to_abbr(), action % 10)
        elif op == BID:
            return 'bid {} {}'.format(suit.to_abbr(), action % 10)
        elif op == BUY:
            return 'buy {}'.format(suit.to_abbr())
        elif op == SELL:
            return 'sell {}'.format(suit.to_abbr())

    def preform(self, action: int) -> None:
        op = action // 100
        action %= 100
        suit = from_value(action // 10)
        if op == ASK:
            self.markets[suit.value].ask(self.active_player, action % 10)
        elif op == BID:
            self.markets[suit.value].bid(self.active_player, action % 10)
        elif op == BUY:
            self.markets[suit.value].buy(self.active_player)
            self.clear_markets()
        elif op == SELL:
            self.markets[suit.value].sell(self.active_player)
            self.clear_markets()

        self.active_player += 1
        if self.active_player == 4:
            self.active_player = 0
            self.round += 1

    def is_finished(self) -> bool:
        return self.round == NUM_ROUNDS

    def get_utility(self) -> np.ndarray:
        utility = np.zeros(4)
        total_awarded = 0
        for i in range(NUM_PLAYERS):
            award = self.cards[i][self.goal_suit.value] * 10
            utility[i] = self.chips[i] + award
            total_awarded += award

        max_goal_cards = max(self.cards[i][self.goal_suit.value] for i in range(NUM_PLAYERS))
        winners = [j for j in range(NUM_PLAYERS) if self.cards[j][self.goal_suit.value] == max_goal_cards]

        prize = (200 - total_awarded) // len(winners)
        for winner in winners:
            utility[winner] += prize

        return utility

    def get_active_player(self) -> int:
        return self.active_player


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
        if amount <= 0 or amount > 9:
            return False, 'amount must be in range (0, 9]'
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
        if amount <= 0 or amount > 9:
            return False, 'amount must be in range (0, 9]'
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
