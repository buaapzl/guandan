"""记牌器模块 - 跟踪已打出的牌"""
from collections import Counter
from typing import Optional

from guandan_core.cards import Card, Rank


class Recorder:
    """记牌器：跟踪已打出的牌"""

    # 每种点数的牌数量（普通牌4张，王牌各1张）
    TOTAL_COUNTS = {
        Rank.THREE: 4, Rank.FOUR: 4, Rank.FIVE: 4, Rank.SIX: 4,
        Rank.SEVEN: 4, Rank.EIGHT: 4, Rank.NINE: 4, Rank.TEN: 4,
        Rank.J: 4, Rank.Q: 4, Rank.K: 4, Rank.A: 4, Rank.TWO: 4,
        Rank.SMALL_JOKER: 1, Rank.BIG_JOKER: 1,
    }

    def __init__(self):
        self.played_cards: list[Card] = []
        self.played_ranks = Counter()  # 各点数已打出的数量

    def record(self, cards: list[Card]):
        """记录已打出的牌"""
        for card in cards:
            self.played_cards.append(card)
            self.played_ranks[card.rank] += 1

    def get_remaining(self, rank: Rank) -> int:
        """获取某点数的剩余数量"""
        total = self.TOTAL_COUNTS.get(rank, 0)
        played = self.played_ranks.get(rank, 0)
        return total - played

    def is_exhausted(self, rank: Rank) -> bool:
        """某点数是否已打完"""
        return self.get_remaining(rank) == 0

    def get_remaining_cards(self) -> dict[Rank, int]:
        """获取所有剩余牌统计"""
        remaining = {}
        for rank in Rank:
            count = self.get_remaining(rank)
            if count > 0:
                remaining[rank] = count
        return remaining

    def reset(self):
        """重置"""
        self.played_cards.clear()
        self.played_ranks.clear()
