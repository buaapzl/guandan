"""算牌器模块 - 估算对手牌概率"""
from typing import Optional

from guandan_core.cards import Rank
from guandan_core.recorder import Recorder


class Calculator:
    """算牌器：根据已知信息估算概率"""

    def __init__(self, recorder: Recorder, my_hand_ranks: set[Rank], num_opponents: int = 3):
        """
        初始化算牌器

        Args:
            recorder: 记牌器实例
            my_hand_ranks: 我手中的牌点数集合
            num_opponents: 对手数量（默认为3，即四人局）
        """
        self.recorder = recorder
        self.my_hand_ranks = my_hand_ranks
        self.num_opponents = num_opponents
        # 每位玩家平均手牌数（54张/4人=13.5，取整为14）
        self.avg_cards_per_player = 14

    def get_opponent_presence_prob(self, rank: Rank) -> float:
        """
        估算对手持有某点数的概率

        计算方法：
        - 已知的某点数牌数 = 已打出的 + 我手中的
        - 剩余该点数牌数 = 总数 - 已知
        - 对手持有概率 = 剩余牌数 / (对手人数 * 平均手牌数)
        """
        # 该点数的总牌数
        total = Recorder.TOTAL_COUNTS.get(rank, 0)

        # 已打出的数量
        played = self.recorder.played_ranks.get(rank, 0)

        # 我手中的数量
        in_my_hand = 1 if rank in self.my_hand_ranks else 0

        # 剩余在牌堆/对手手中的数量
        remaining = total - played - in_my_hand

        if remaining <= 0:
            return 0.0

        # 估算对手持有的概率
        # 假设剩余牌随机分布在对手手中
        opponent_cards = self.num_opponents * self.avg_cards_per_player
        prob = remaining / opponent_cards

        # 最多为1.0
        return min(prob, 1.0)

    def get_dangerous_ranks(self, threshold: float = 0.5) -> list[Rank]:
        """
        获取危险的点数（对手很可能有）

        Args:
            threshold: 概率阈值，默认0.5

        Returns:
            按概率降序的危险点数列表
        """
        dangerous = []
        for rank in Rank:
            prob = self.get_opponent_presence_prob(rank)
            if prob >= threshold:
                dangerous.append((rank, prob))

        # 按概率降序排序
        dangerous.sort(key=lambda x: x[1], reverse=True)
        return [rank for rank, _ in dangerous]

    def suggest_play(self, playable_combos: list) -> list:
        """
        建议出牌（简化版）

        策略：
        1. 优先打出剩余少或已打光的点数（相对安全）
        2. 避免打出危险点数（对手很可能有大牌）

        Args:
            playable_combos: 可出的牌型列表

        Returns:
            推荐的出牌列表（按优先级排序）
        """
        if not playable_combos:
            return []

        # 计算每个牌型的"安全度"
        # 安全度 = 已打出的数量 + 我手中的数量
        scored_combos = []
        for combo in playable_combos:
            # 获取该牌型涉及的所有点数
            ranks = set()
            if isinstance(combo, list):
                for card in combo:
                    ranks.add(card.rank)
            else:
                ranks.add(combo.rank)

            # 计算安全度分数
            safety_score = 0
            for rank in ranks:
                total = Recorder.TOTAL_COUNTS.get(rank, 0)
                played = self.recorder.played_ranks.get(rank, 0)
                in_my_hand = 1 if rank in self.my_hand_ranks else 0
                # 越接近打完越安全
                safety_score += (played + in_my_hand) / total if total > 0 else 0

            # 平均安全度
            avg_safety = safety_score / len(ranks) if ranks else 0
            scored_combos.append((combo, avg_safety))

        # 按安全度降序排序
        scored_combos.sort(key=lambda x: x[1], reverse=True)
        return [combo for combo, _ in scored_combos]
