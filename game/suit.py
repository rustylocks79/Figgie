from enum import Enum


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