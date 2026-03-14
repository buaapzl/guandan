import pytest
from guandan_core.cards import Card, CardType, Suit, Rank

def test_card_creation():
    card = Card(Rank.A, Suit.SPADE)
    assert card.rank == Rank.A
    assert card.suit == Suit.SPADE

def test_card_comparison():
    c1 = Card(Rank.A, Suit.SPADE)
    c2 = Card(Rank.K, Suit.SPADE)
    assert c1 > c2
    assert c2 < c1

def test_joker():
    small_joker = Card(Rank.SMALL_JOKER, None)
    big_joker = Card(Rank.BIG_JOKER, None)
    assert small_joker < big_joker

def test_card_to_index():
    card = Card(Rank.A, Suit.SPADE)
    assert card.to_index() == 0

def test_index_to_card():
    card = Card.from_index(0)
    assert card.rank == Rank.A
    assert card.suit == Suit.SPADE
