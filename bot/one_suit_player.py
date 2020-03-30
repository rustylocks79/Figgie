from figgie import Player, Suit


class OneSuitPlayer(Player):
    def __init__(self, name, game):
        super().__init__(name, game)

    def get_target_suit(self) -> Suit:
        return max(self.cards, key=self.cards.get)

    def on_turn(self, verbose=False):
        target_suit = self.get_target_suit()
        if self.get_selling_price(target_suit) is None:
            if target_suit != Suit.DIAMONDS and self.cards[Suit.DIAMONDS] > 0:
                self.ask(Suit.DIAMONDS, 9, verbose)
            if target_suit != Suit.CLUBS and self.cards[Suit.CLUBS] > 0:
                self.ask(Suit.CLUBS, 9, verbose)
            if target_suit != Suit.HEARTS and self.cards[Suit.HEARTS] > 0:
                self.ask(Suit.HEARTS, 9, verbose)
            if target_suit != Suit.SPADES and self.cards[Suit.SPADES] > 0:
                self.ask(Suit.SPADES, 9, verbose)
        else:
            self.buy(target_suit, verbose)
