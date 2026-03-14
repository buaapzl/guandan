from enum import IntEnum
from typing import Optional


class Suit(IntEnum):
    """花色枚举"""
    SPADE = 1
    HEART = 2
    CLUB = 3
    DIAMOND = 4
    JOKER = 5


class Rank(IntEnum):
    """点数枚举"""
    A = 1
    K = 2
    Q = 3
    J = 4
    TEN = 5
    NINE = 6
    EIGHT = 7
    SEVEN = 8
    SIX = 9
    FIVE = 10
    FOUR = 11
    THREE = 12
    TWO = 13
    SMALL_JOKER = 14
    BIG_JOKER = 15


class CardType(IntEnum):
    """牌型枚举"""
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    TRIPLE_PAIR = 4
    STRAIGHT = 5
    CONTINUOUS_PAIR = 6
    AIRPLANE = 7
    STEEL_PLATE = 8
    BOMB = 9
    SOFT_BOMB = 10
    KING_BOMB = 11


class Card:
    """扑克牌类"""

    # 花色符号映射
    SUIT_SYMBOLS = {
        Suit.SPADE: '♠',
        Suit.HEART: '♥',
        Suit.CLUB: '♣',
        Suit.DIAMOND: '♦',
    }

    # 点数中文映射
    RANK_NAMES = {
        Rank.SMALL_JOKER: '小王',
        Rank.BIG_JOKER: '大王',
        Rank.THREE: '3',
        Rank.FOUR: '4',
        Rank.FIVE: '5',
        Rank.SIX: '6',
        Rank.SEVEN: '7',
        Rank.EIGHT: '8',
        Rank.NINE: '9',
        Rank.TEN: '10',
        Rank.J: 'J',
        Rank.Q: 'Q',
        Rank.K: 'K',
        Rank.A: 'A',
        Rank.TWO: '2',
    }

    def __init__(self, rank: Rank, suit: Optional[Suit]):
        self.rank = rank
        self.suit = suit

    @property
    def is_joker(self) -> bool:
        """是否为大小王"""
        return self.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)

    def to_index(self) -> int:
        """
        转换为索引 0-53
        0-51: 普通牌 (按点数和花色)
        52: 小王
        53: 大王
        """
        if self.rank == Rank.SMALL_JOKER:
            return 52
        elif self.rank == Rank.BIG_JOKER:
            return 53
        else:
            # 普通牌: (rank - 1) * 4 + (suit - 1)
            return (self.rank - 1) * 4 + (self.suit - Suit.SPADE)

    @classmethod
    def from_index(cls, index: int) -> 'Card':
        """
        从索引创建牌
        0-51: 普通牌
        52: 小王
        53: 大王
        """
        if index == 52:
            return cls(Rank.SMALL_JOKER, None)
        elif index == 53:
            return cls(Rank.BIG_JOKER, None)
        else:
            # rank = index // 4 + 1
            rank = index // 4 + 1
            suit = Suit.SPADE + index % 4
            return cls(Rank(rank), suit)

    def _get_sort_value(self) -> int:
        """获取排序值，值越大牌越大"""
        if self.rank == Rank.SMALL_JOKER:
            return 100 + 1
        elif self.rank == Rank.BIG_JOKER:
            return 100 + 2
        else:
            # 普通牌：rank 值越小牌越大（反转）
            return 20 - self.rank.value

    def __lt__(self, other: 'Card') -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self._get_sort_value() < other._get_sort_value()

    def __gt__(self, other: 'Card') -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self._get_sort_value() > other._get_sort_value()

    def __hash__(self):
        return hash(self.to_index())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.to_index() == other.to_index()

    def __repr__(self) -> str:
        if self.rank == Rank.SMALL_JOKER:
            return '小王'
        elif self.rank == Rank.BIG_JOKER:
            return '大王'
        else:
            suit_symbol = self.SUIT_SYMBOLS.get(self.suit, '')
            rank_name = self.RANK_NAMES.get(self.rank, '')
            return f'{suit_symbol}{rank_name}'


def create_deck() -> list[Card]:
    """
    创建一副54张牌
    """
    deck = []
    # 普通牌: 52张
    for rank in range(Rank.THREE, Rank.TWO + 1):
        for suit in range(Suit.SPADE, Suit.DIAMOND + 1):
            deck.append(Card(Rank(rank), Suit(suit)))
    # 大小王: 2张
    deck.append(Card(Rank.SMALL_JOKER, None))
    deck.append(Card(Rank.BIG_JOKER, None))
    return deck
