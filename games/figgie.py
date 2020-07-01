from enum import Enum
from random import *


class Suit(Enum):
    DIAMONDS = 0
    CLUBS = 1
    HEARTS = 2
    SPADES = 3

    def opposite(self):
        if self.value == Suit.DIAMONDS.value:
            return Suit.HEARTS
        elif self.value == Suit.CLUBS.value:
            return Suit.CLUBS
        elif self.value == Suit.HEARTS.value:
            return Suit.DIAMONDS
        elif self.value == Suit.SPADES.value:
            return Suit.CLUBS


SUITS = [Suit.DIAMONDS, Suit.CLUBS, Suit.HEARTS, Suit.SPADES]


class Figgie:
    def __init__(self):
        self.players = []
        self.goal_suit = Suit.HEARTS
        self.markets = []
        self.starting_chips = 250
        for i in range(len(SUITS)):
            self.markets.append(Market(SUITS[i]))

    def reset(self):
        for market in self.markets:
            market.clear()
        for player in self.players:
            player.reset()
        self.deal()

    def deal(self):
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

        assert len(self.players) == 4
        for i in range(4):
            for j in range(10):
                suit = deck.pop()
                self.players[i].cards[suit] += 1

        for player in self.players:
            player.on_deal()

    def deal_exact(self, cards_list):
        for i in range(4):
            self.players[i].cards = cards_list[i]

    def clear_markets(self):
        for market in self.markets:
            market.clear()

    def play_round(self, rounds, verbose=False):
        for round in range(rounds):
            shuffled_players = sample(self.players, len(self.players))
            for player in shuffled_players:
                player.on_turn(verbose)

    def get_winners(self) -> list:
        awarded = 0
        for player in self.players:
            winnings = player.cards[self.goal_suit] * 10
            player.chips += winnings
            awarded += winnings

        winners = [p for p in self.players if p.cards[self.goal_suit] == max(player.cards[self.goal_suit] for player in self.players)]

        remaining_winnings = 200 - awarded
        for winner in winners:
            winner.chips += remaining_winnings // len(winners)

        return winners

    def add_chips(self, chips):
        for i in range(len(self.players)):
            self.players[i].chips += chips[i]

    def print_all(self):
        for player in self.players:
            print('{} has {} chips and hand: '.format(player.name, player.chips,), end='')
            for key in player.cards:
                print('{}: {}, '.format(key.name, player.cards[key]), end='')
            print()

    def play_games(self, num_games=1, rounds_per_game=5, verbose=False) -> dict:
        wins = {self.players[0]: 0, self.players[1]: 0, self.players[2]: 0, self.players[3]: 0}
        for game in range(num_games):
            self.reset()

            if verbose:
                print('Initial Hands: ')
                self.print_all()

            self.play_round(rounds_per_game, verbose)
            winners = self.get_winners()

            if verbose:
                print('\nPlayed {} round(s). \n'.format(rounds_per_game))
                print('Results: ')
                print('The goal suit was {}'.format(self.goal_suit.name))
                self.print_all()
                if len(winners) == 2:
                    print('{} and {} have won the game. '.format(winners[0].name, winners[1].name))
                else:
                    print('{} has won the game. '.format(winners[0].name))
                print()

            for winner in winners:
                wins[winner] += 1

        if verbose:
            for player in wins.keys():
                print('{} won {} games. '.format(player.name, wins[player]))
        return wins


class Market:
    def __init__(self, suit):
        self.buying_price = None
        self.buying_player = None
        self.selling_price = None
        self.selling_player = None
        self.suit = suit

    def ask(self, amount, player):
        if player.cards[self.suit] < 1:
            raise ValueError('player({}) can not set an asking price for a card he does not have. '.format(player.name))

        if self.selling_price is None or amount < self.selling_price:
            self.selling_price = amount
            self.selling_player = player

    def bid(self, amount, player):
        if player.chips < amount:
            raise ValueError('player({}) can not bid {} chips because he only has {}. '
                             .format(player.name, amount, player.chips))

        if self.buying_price is None or amount > self.buying_price :
            self.buying_price = amount
            self.buying_player = player

    def at(self, buying_price, selling_price, player):
        if buying_price >= selling_price:
            raise ValueError('player({}) can not {} at {} because buying price must be less than selling price. '
                             .format(player.name, buying_price, selling_price))
        self.bid(buying_price, player)
        self.ask(selling_price, player)

    def buy(self, player):
        if player is self.buying_player:
            raise ValueError('player({}) can not buy from themselves. '.format(player.name))
        if self.selling_price is None:
            raise ValueError('player({}) can not buy suit({}) because no one has set an asking price. '
                             .format(player.name, self.suit))
        if player.chips < self.selling_price:
            raise ValueError('player({}) can not buy suit({}) from player({}) because he has less than {} chips'
                             .format(player.name, self.suit, self.selling_player.name, player.chips))
        if self.selling_player.cards[self.suit] < 1:
            raise ValueError('player({}) can not buy suit({}) from player({}) because the selling player does not have the card'
                             .format(player.name, self.suit, self.selling_player.name))

        self.selling_player.chips += self.selling_price
        self.selling_player.cards[self.suit] -= 1

        player.chips -= self.selling_price
        player.cards[self.suit] += 1

    def sell(self, player):
        if player is self.selling_player:
            raise ValueError('player({}) can not sell to themselves. '.format(player.name))
        if self.buying_price is None:
            raise ValueError('player({}) can not sell suit({}) because no one has set an bidding price. '
                             .format(player.name, self.suit))
        if self.buying_player.chips < self.buying_price:
            raise ValueError('player({}) can not sell suit({}) to player({}) because he has less than {} chips'
                             .format(player.name, self.suit, self.buying_player.name, player.chips))
        if self.buying_player.cards[self.suit] < 1:
            raise ValueError('player({}) can not sell suit({}) to player({}) because the selling player does not have the card'
                             .format(player.name, self.suit, self.buying_player.name))

        player.chips += self.buying_price
        player.cards[self.suit] -= 1

        self.buying_player.chips -= self.buying_price
        self.buying_player.cards[self.suit] += 1

    def clear(self):
        self.buying_price = None
        self.buying_player = None
        self.selling_price = None
        self.selling_player = None


class Player:
    def __init__(self, name, game):
        self.name = name
        self.__game = game
        self.chips = game.starting_chips
        self.cards = {Suit.CLUBS: 0, Suit.DIAMONDS: 0, Suit.HEARTS: 0, Suit.SPADES: 0}

    def reset(self):
        self.chips = self.__game.starting_chips
        self.cards = {Suit.CLUBS: 0, Suit.DIAMONDS: 0, Suit.HEARTS: 0, Suit.SPADES: 0}

    def ask(self, suit, amount, verbose=False):
        self.__game.markets[suit.value].ask(amount, self)
        if verbose:
            print('{}: asked for {} for {}'.format(self.name, suit.name, amount))

    def bid(self, suit, amount, verbose=False):
        self.__game.markets[suit.value].bid(amount, self)
        if verbose:
            print('{}: bid on {} for {}'.format(self.name, suit.name, amount))

    def at(self, suit, buying_price, selling_price, verbose=False):
        self.__game.markets[suit.value].at(buying_price, selling_price, self)
        if verbose:
            print('{}: {} at {} for {}'.format(self.name, buying_price, selling_price, suit.name))

    def get_buying_price(self, suit) -> int:
        return self.__game.markets[suit.value].buying_price

    def get_buying_player(self, suit):
        return self.__game.markets[suit.value].buying_player

    def buy(self, suit, verbose=False):
        self.__game.markets[suit.value].buy(self)
        if verbose:
            print('{} bought {} from {} for {}'.format(self.name, suit.name,
                                                       self.__game.markets[suit.value].selling_player.name, self.__game.markets[suit.value].selling_price))
        self.__game.clear_markets()

    def get_selling_price(self, suit) -> int:
        return self.__game.markets[suit.value].selling_price

    def get_selling_player(self, suit):
        return self.__game.markets[suit.value].selling_player

    def sell(self, suit, verbose=False):
        self.__game.markets[suit.value].sell(self)
        if verbose:
            print('{} sold {} to {} for {}'.format(self.name, suit.name,
                                                   self.__game.markets[suit.value].buying_player.name, self.__game.markets[suit.value].buying_price))
        self.__game.clear_markets()

    def on_deal(self):
        pass

    def on_turn(self, verbose=False):
        pass


class ControlledPlayer(Player):
    def __init__(self, name, game):
        super().__init__(name, game)
