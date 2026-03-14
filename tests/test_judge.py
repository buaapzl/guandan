import pytest
from guandan_core.cards import Card, CardType, Rank, Suit
from guandan_core.judge import identify_card_type, compare_card_types

def test_identify_single():
    cards = [Card(Rank.A, Suit.SPADE)]
    assert identify_card_type(cards) == CardType.SINGLE

def test_identify_pair():
    cards = [Card(Rank.A, Suit.SPADE), Card(Rank.A, Suit.HEART)]
    assert identify_card_type(cards) == CardType.PAIR

def test_identify_triple():
    cards = [Card(Rank.A, Suit.SPADE), Card(Rank.A, Suit.HEART), Card(Rank.A, Suit.CLUB)]
    assert identify_card_type(cards) == CardType.TRIPLE

def test_identify_straight():
    cards = [Card(Rank.THREE, Suit.SPADE), Card(Rank.FOUR, Suit.HEART),
             Card(Rank.FIVE, Suit.CLUB), Card(Rank.SIX, Suit.DIAMOND),
             Card(Rank.SEVEN, Suit.SPADE)]
    assert identify_card_type(cards) == CardType.STRAIGHT

def test_identify_bomb():
    cards = [Card(Rank.A, Suit.SPADE), Card(Rank.A, Suit.HEART),
             Card(Rank.A, Suit.CLUB), Card(Rank.A, Suit.DIAMOND)]
    assert identify_card_type(cards) == CardType.BOMB

def test_identify_king_bomb():
    cards = [Card(Rank.SMALL_JOKER, None), Card(Rank.BIG_JOKER, None)]
    assert identify_card_type(cards) == CardType.KING_BOMB

def test_compare_bomb_vs_single():
    bomb = [Card(Rank.A, Suit.SPADE), Card(Rank.A, Suit.HEART),
            Card(Rank.A, Suit.CLUB), Card(Rank.A, Suit.DIAMOND)]
    single = [Card(Rank.K, Suit.SPADE)]
    assert compare_card_types(bomb, single) > 0
