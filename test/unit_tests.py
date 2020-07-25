import unittest

import numpy as np

from games.figgie import Figgie, Suit, STARTING_CHIPS, SUITS, ASK, BID, BUY, SELL


class Testing(unittest.TestCase):

    def setUp(self) -> None:
        pass
        self.game = Figgie()
        self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_ask(self):
        def check(suit: Suit):
            self.game.cards[0][suit.value] = 0
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertFalse(can)

            self.game.cards[0][suit.value] = 2
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertTrue(can)

            self.game.preform((ASK * 100) + (suit.value * 10) + 7)
            self.assertEqual(self.game.markets[suit.value].selling_price, 7, 'Selling price not set properly with ask operation')

        for suit in SUITS:
            check(suit)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_bid(self):
        def check(suit: Suit):
            can, _ = self.game.markets[suit.value].can_bid(0, 7)
            self.assertTrue(can)

            self.game.preform((BID * 100) + (suit.value * 10) + 7)
            self.assertEqual(self.game.markets[suit.value].buying_price, 7,
                             'Buying price not set properly with ask operation')

        for suit in SUITS:
            check(suit)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_buy(self):
        def check(suit: Suit):
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertTrue(can)
            self.game.preform((ASK * 100) + (suit.value * 10) + 7)
            self.assertEqual(self.game.markets[suit.value].selling_price, 7,
                             'Selling price not set properly with ask operation')

            self.game.preform((BUY * 100) + (suit.value * 10))
            for s in SUITS:
                self.assertEqual(self.game.markets[s.value].buying_price, None,
                                 'Market not reset after buy')
                self.assertEqual(self.game.markets[s.value].selling_price, None,
                                 'Market not reset after buy')
            self.assertEqual(self.game.chips[1], STARTING_CHIPS - 7, 'Chips not properly subtracted')
            self.assertEqual(self.game.chips[0], STARTING_CHIPS + 7, 'Chips not properly added')
            self.assertEqual(self.game.cards[1][suit.value], 3, 'card not properly added')
            self.assertEqual(self.game.cards[0][suit.value], 1, 'card not properly subtracted')

        for suit in SUITS:
            check(suit)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_sell(self):
        def check(suit: Suit):
            can, _ = self.game.markets[suit.value].can_bid(0, 7)
            self.assertTrue(can)

            self.game.preform((BID * 100) + (suit.value * 10) + 7)
            self.assertEqual(self.game.markets[suit.value].buying_price, 7,
                             'Buying price not set properly with ask operation')
            self.game.preform((SELL * 100) + (suit.value * 10))
            for s in SUITS:
                self.assertEqual(self.game.markets[s.value].buying_price, None,
                                 'Market not reset after buy')
                self.assertEqual(self.game.markets[s.value].selling_price, None,
                                 'Market not reset after buy')
            self.assertEqual(self.game.chips[0], STARTING_CHIPS - 7, 'Chips not properly subtracted')
            self.assertEqual(self.game.chips[1], STARTING_CHIPS + 7, 'Chips not properly added')
            self.assertEqual(self.game.cards[0][suit.value], 3, 'card not properly added')
            self.assertEqual(self.game.cards[1][suit.value], 1, 'card not properly subtracted')

        for suit in SUITS:
            check(suit)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)
