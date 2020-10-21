import unittest

import numpy as np

from figgie import Figgie, STARTING_CHIPS, SUITS, Action, Suit
from util import info_sets


class Tests(unittest.TestCase):
    def test_deal(self):
        figgie = Figgie()

        for i in range(10):
            figgie.deal()
            total_cards = figgie.cards[0] + figgie.cards[1] + figgie.cards[2] + figgie.cards[3]
            self.assertTrue(total_cards[figgie.goal_suit.value] == 8 or total_cards[figgie.goal_suit.value] == 10)
            self.assertEqual(12, total_cards[figgie.goal_suit.opposite().value])
            self.assertEqual(40, np.sum(total_cards))

    def test_ask(self):
        figgie = Figgie()
        for suit in SUITS:
            figgie.cards = np.full((4, 4), 2, dtype=int)

            player = figgie.active_player
            hand = figgie.cards[player]
            market = figgie.markets[suit.value]

            hand[suit.value] = 0
            can, _ = market.can_ask(player, 7)
            self.assertFalse(can)
            can, _ = figgie.can_preform(Action.ask(suit, 7))
            self.assertFalse(can)

            hand[suit.value] = 2
            can, _ = market.can_ask(player, 7)
            self.assertTrue(can)
            can, _ = figgie.can_preform(Action.ask(suit, 7))
            self.assertTrue(can)

            figgie.preform(Action.ask(suit, 7))
            self.assertEqual(7, market.selling_price,
                             'Selling price not set properly with ask operation')
            self.assertEqual(Action.ask(suit, 7), figgie.history[-1])
            self.assertEqual(1, market.operations)
            figgie.reset()

    def test_bid(self):
        figgie = Figgie()
        for suit in SUITS:
            figgie.cards = np.full((4, 4), 2, dtype=int)

            player = figgie.active_player
            market = figgie.markets[suit.value]

            can, _ = market.can_bid(player, 7)
            self.assertTrue(can)
            can, _ = figgie.can_preform(Action.bid(suit, 7))
            self.assertTrue(can)

            figgie.preform(Action.bid(suit, 7))
            self.assertEqual(7, market.buying_price,
                             'Buying price not set properly with bid operation')
            self.assertEqual(Action.bid(suit, 7), figgie.history[-1])
            self.assertEqual(1, market.operations)
            figgie.reset()

    def test_buy(self):
        figgie = Figgie()
        for suit in SUITS:
            figgie.cards = np.full((4, 4), 2, dtype=int)

            player = figgie.active_player
            market = figgie.markets[suit.value]

            can, _ = market.can_ask(0, 7)
            self.assertTrue(can)
            asking_player = player
            figgie.preform(Action.ask(suit, 7))
            self.assertEqual(7, market.selling_price,
                             'Selling price not set properly with ask operation')
            self.assertEqual(1, market.operations)

            if figgie.active_player == asking_player:
                figgie.preform(Action.passing())

            player = figgie.active_player

            figgie.preform(Action.buy(suit))
            for s in SUITS:
                self.assertEqual(figgie.markets[s.value].buying_price, None, 'Market not reset after buy')
                self.assertEqual(figgie.markets[s.value].selling_price, None, 'Market not reset after buy')
            self.assertEqual(STARTING_CHIPS - 7, figgie.chips[player], 'Chips not properly subtracted')
            self.assertEqual(STARTING_CHIPS + 7, figgie.chips[asking_player], 'Chips not properly added')
            self.assertEqual(3, figgie.cards[player][suit.value], 'card not properly added')
            self.assertEqual(1, figgie.cards[asking_player][suit.value], 'card not properly subtracted')
            self.assertEqual(1, market.transactions)
            self.assertEqual(7, market.last_price)
            self.assertEqual(2, market.operations)

            figgie.reset()

    def test_sell(self):
        figgie = Figgie()
        for suit in SUITS:
            figgie.cards = np.full((4, 4), 2, dtype=int)
            player = figgie.active_player
            market = figgie.markets[suit.value]

            can, _ = market.can_bid(0, 7)
            self.assertTrue(can)
            bidding_player = player
            figgie.preform(Action.bid(suit, 7))
            self.assertEqual(7, market.buying_price, 'Buying price not set properly with ask operation')
            self.assertEqual(1, market.operations)

            if figgie.active_player == bidding_player:
                figgie.preform(Action.passing())

            player = figgie.active_player

            figgie.preform(Action.sell(suit))
            for s in SUITS:
                self.assertEqual(figgie.markets[s.value].buying_price, None, 'Market not reset after sell')
                self.assertEqual(figgie.markets[s.value].selling_price, None, 'Market not reset after sell')
            self.assertEqual(STARTING_CHIPS - 7, figgie.chips[bidding_player], 'Chips not properly subtracted')
            self.assertEqual(STARTING_CHIPS + 7,figgie.chips[player], 'Chips not properly added')
            self.assertEqual(3, figgie.cards[bidding_player][suit.value], 'card not properly added')
            self.assertEqual(1, figgie.cards[player][suit.value], 'card not properly subtracted')
            self.assertEqual(1, market.transactions)
            self.assertEqual(7, market.last_price)
            self.assertEqual(2, market.operations)
            figgie.reset()

    def test_win(self):
        figgie = Figgie()
        figgie.goal_suit = Suit.SPADES
        figgie.cards = np.array([[12, 0, 0, 0], [0, 10, 0, 0], [0, 0, 8, 0], [0, 0, 0, 10]])
        results = figgie.get_utility()
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
