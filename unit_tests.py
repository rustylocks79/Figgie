import unittest
from figgie import *


class Testing(unittest.TestCase):

    def setUp(self) -> None:
        self.game = Figgie()
        player1 = Player('player 1', self.game)
        player1.chips = 250

        player2 = Player('player 2', self.game)
        player2.chips = 250

        player3 = Player('player 3', self.game)
        player3.chips = 250

        player4 = Player('player 4', self.game)
        player4.chips = 250

        self.game.players.append(player1)
        self.game.players.append(player2)
        self.game.players.append(player3)
        self.game.players.append(player4)
        self.game.deal_exact([
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2}
        ])

    def test_ask(self):
        player = self.game.players[0]
        player.cards = {Suit.CLUBS: 0, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2}
        with self.assertRaises(ValueError):
            player.ask(Suit.CLUBS, 7)

    def test_bid(self):
        player = self.game.players[0]
        player.chips = 2
        with self.assertRaises(ValueError):
            player.bid(Suit.CLUBS, 3)
