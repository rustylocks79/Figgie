import unittest

from figgie import Figgie, Suit


class Testing(unittest.TestCase):

    def setUp(self) -> None:
        pass
        self.game = Figgie()
        self.game.cards = [
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2},
            {Suit.CLUBS: 2, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2}
        ]

    def test_ask(self):
        pass
        # player = self.game.players[0]
        # player.cards = {Suit.CLUBS: 0, Suit.DIAMONDS: 2, Suit.HEARTS: 2, Suit.SPADES: 2}
        # with self.assertRaises(ValueError):
        #     player.ask(Suit.CLUBS, 7)

    def test_bid(self):
        pass
        # player = self.game.players[0]
        # player.chips = 2
        # with self.assertRaises(ValueError):
        #     player.bid(Suit.CLUBS, 3)

    def test_buy(self):
        pass

    def test_sell(self):
        pass
