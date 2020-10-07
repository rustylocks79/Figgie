import unittest

import numpy as np

from game.action.ask_action import AskAction
from game.action.bid_action import BidAction
from game.action.buy_action import BuyAction
from game.action.pass_action import PassAction
from game.action.sell_action import SellAction
from game.figgie import Figgie, STARTING_CHIPS, SUITS
from game.suit import Suit
from util import info_sets


class Testing(unittest.TestCase):

    def setUp(self) -> None:
        pass
        self.game = Figgie()
        self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_ask(self):
        for suit in SUITS:
            self.game.cards[0][suit.value] = 0
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertFalse(can)

            self.game.cards[0][suit.value] = 2
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertTrue(can)

            self.game.preform(AskAction(suit, 7))
            self.assertEqual(self.game.markets[suit.value].selling_price, 7,
                             'Selling price not set properly with ask operation')
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_bid(self):
        for suit in SUITS:
            can, _ = self.game.markets[suit.value].can_bid(0, 7)
            self.assertTrue(can)

            self.game.preform(BidAction(suit, 7))
            self.assertEqual(self.game.markets[suit.value].buying_price, 7,
                             'Buying price not set properly with ask operation')
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_buy(self):
        for suit in SUITS:
            can, _ = self.game.markets[suit.value].can_ask(0, 7)
            self.assertTrue(can)
            asking_player = self.game.active_player
            self.game.preform(AskAction(suit, 7))
            self.assertEqual(self.game.markets[suit.value].selling_price, 7,
                             'Selling price not set properly with ask operation')

            buying_player = self.game.active_player
            if buying_player == asking_player:
                self.game.preform(PassAction(buying_player))
                buying_player = self.game.active_player
            self.game.preform(BuyAction(suit))
            for s in SUITS:
                self.assertEqual(self.game.markets[s.value].buying_price, None,
                                 'Market not reset after buy')
                self.assertEqual(self.game.markets[s.value].selling_price, None,
                                 'Market not reset after buy')
            self.assertEqual(STARTING_CHIPS - 7, self.game.chips[buying_player], 'Chips not properly subtracted')
            self.assertEqual(STARTING_CHIPS + 7, self.game.chips[asking_player], 'Chips not properly added')
            self.assertEqual(3, self.game.cards[buying_player][suit.value], 'card not properly added')
            self.assertEqual(1, self.game.cards[asking_player][suit.value], 'card not properly subtracted')
            self.assertEqual(1, self.game.markets[suit.value].transactions)
            self.assertEqual(7, self.game.markets[suit.value].last_price_bought)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_sell(self):
        for suit in SUITS:
            can, _ = self.game.markets[suit.value].can_bid(0, 7)
            self.assertTrue(can)
            bidding_player = self.game.active_player
            self.game.preform(BidAction(suit, 7))
            self.assertEqual(7, self.game.markets[suit.value].buying_price,
                             'Buying price not set properly with ask operation')
            self.assertEqual(1, self.game.markets[suit.value].operations)
            selling_player = self.game.active_player
            if selling_player == bidding_player:
                self.game.preform(PassAction(selling_player))
                selling_player = self.game.active_player
            self.game.preform(SellAction(suit))
            for s in SUITS:
                self.assertEqual(self.game.markets[s.value].buying_price, None,
                                 'Market not reset after sell')
                self.assertEqual(self.game.markets[s.value].selling_price, None,
                                 'Market not reset after sell')
            self.assertEqual(STARTING_CHIPS - 7, self.game.chips[bidding_player], 'Chips not properly subtracted')
            self.assertEqual(STARTING_CHIPS + 7, self.game.chips[selling_player], 'Chips not properly added')
            self.assertEqual(3, self.game.cards[bidding_player][suit.value], 'card not properly added')
            self.assertEqual(1, self.game.cards[selling_player][suit.value], 'card not properly subtracted')
            self.assertEqual(1, self.game.markets[suit.value].transactions)
            self.assertEqual(7, self.game.markets[suit.value].last_price_sold)
            self.assertEqual(2, self.game.markets[suit.value].operations)
            self.game.reset()
            self.game.cards = np.full((4, 4), 2, dtype=int)

    def test_win(self):
        self.game.goal_suit = Suit.SPADES
        self.game.cards = np.array([[12, 0, 0, 0], [0, 10, 0, 0], [0, 0, 8, 0], [0, 0, 0, 10]])
        results = self.game.get_utility()
        self.assertEqual([250, 250, 250, 450], results.tolist())

    def test_names(self):
        self.assertEqual('std', info_sets['std'].name)
        self.assertEqual('h', info_sets['h'].name)
        self.assertEqual('t', info_sets['t'].name)
        self.assertEqual('l', info_sets['l'].name)
        self.assertEqual('ht', info_sets['ht'].name)
        self.assertEqual('hl', info_sets['hl'].name)
        self.assertEqual('tl', info_sets['tl'].name)
        self.assertEqual('htl', info_sets['htl'].name)
