"""
玩家类
"""
from collections import Counter
from typing import Optional

from guandan_core.cards import Card, CardType, Rank, Suit
from guandan_core.judge import identify_card_type


class Player:
    """玩家类"""

    # 位置名称映射
    POSITION_NAMES = {
        0: '南',
        1: '西',
        2: '北',
        3: '东',
    }

    def __init__(self, player_id: int, name: str = ""):
        self.player_id = player_id
        self.name = name or f"Player{player_id}"
        self.hand: list[Card] = []
        self.position: int = player_id  # 0=南, 1=西, 2=北, 3=东

    @property
    def position_name(self) -> str:
        """获取位置名称"""
        return self.POSITION_NAMES.get(self.position, '')

    @property
    def is_empty(self) -> bool:
        """是否手牌为空"""
        return len(self.hand) == 0

    def receive_card(self, card: Card):
        """收牌"""
        self.hand.append(card)
        self.hand.sort()

    def receive_cards(self, cards: list[Card]):
        """批量收牌"""
        self.hand.extend(cards)
        self.hand.sort()

    def remove_cards(self, cards: list[Card]) -> bool:
        """出牌"""
        for c in cards:
            if c in self.hand:
                self.hand.remove(c)
            else:
                return False
        return True

    def get_playable_cards(self) -> list[list[Card]]:
        """
        获取所有可出的牌型组合
        包括：单张、对子、三张、炸弹等
        """
        if not self.hand:
            return []

        results = []

        # 按点数分组
        rank_groups: dict[Rank, list[Card]] = {}
        for card in self.hand:
            if card.rank not in rank_groups:
                rank_groups[card.rank] = []
            rank_groups[card.rank].append(card)

        # 单张
        for card in self.hand:
            results.append([card])

        # 对子（至少2张相同点数）
        for rank, cards in rank_groups.items():
            if len(cards) >= 2:
                results.append(cards[:2])

        # 三张（至少3张相同点数）
        for rank, cards in rank_groups.items():
            if len(cards) >= 3:
                results.append(cards[:3])

        # 炸弹（4张及以上相同点数）
        for rank, cards in rank_groups.items():
            if len(cards) >= 4:
                # 4张炸弹
                results.append(cards[:4])
                # 5张及以上炸弹
                for i in range(5, len(cards) + 1):
                    results.append(cards[:i])

        # 天王炸弹（大小王）
        jokers = [c for c in self.hand if c.is_joker]
        if len(jokers) >= 2:
            results.append(jokers[:2])

        # 获取所有可能的顺子
        results.extend(self._get_straights())

        # 获取所有可能的连对
        results.extend(self._get_continuous_pairs())

        # 获取所有可能的三带二
        results.extend(self._get_triple_pairs())

        # 获取所有可能的飞机
        results.extend(self._get_airplanes())

        # 获取所有可能的钢板
        results.extend(self._get_steel_plates())

        # 去重并验证牌型
        valid_results = []
        seen = set()
        for cards in results:
            card_type = identify_card_type(cards)
            if card_type != CardType.SINGLE or len(cards) == 1:
                # 按牌的索引排序作为唯一标识
                key = tuple(c.to_index() for c in sorted(cards, key=lambda x: x.to_index()))
                if key not in seen:
                    seen.add(key)
                    valid_results.append(cards)

        return valid_results

    def _get_straights(self) -> list[list[Card]]:
        """获取所有可能的顺子（5张及以上连续点数）"""
        results = []

        # 排除大小王，按点数分组
        normal_cards = [c for c in self.hand if not c.is_joker]
        if len(normal_cards) < 5:
            return results

        # 按点数统计
        rank_counts = Counter(c.rank for c in normal_cards)
        unique_ranks = sorted(set(c.rank for c in normal_cards), key=lambda r: r.value)

        # 尝试从每个点数开始找顺子
        for start_idx in range(len(unique_ranks)):
            straight_ranks = [unique_ranks[start_idx]]

            for i in range(start_idx + 1, len(unique_ranks)):
                # 检查是否连续（考虑A-K循环）
                prev_rank = straight_ranks[-1]
                curr_rank = unique_ranks[i]

                if curr_rank.value - prev_rank.value == 1:
                    straight_ranks.append(curr_rank)
                elif prev_rank.value == 13 and curr_rank.value == 1:  # K-A
                    straight_ranks.append(curr_rank)
                else:
                    break

                # 如果有5张及以上，生成组合
                if len(straight_ranks) >= 5:
                    # 生成所有可能的顺子组合
                    for length in range(5, len(straight_ranks) + 1):
                        for start in range(len(straight_ranks) - length + 1):
                            selected_ranks = straight_ranks[start:start + length]
                            # 对每个点数选取一张牌
                            straight_cards = []
                            for rank in selected_ranks:
                                # 选取该点数的牌（取第一张）
                                for card in self.hand:
                                    if card.rank == rank and not card.is_joker:
                                        straight_cards.append(card)
                                        break
                            if len(straight_cards) == length:
                                results.append(straight_cards)

        return results

    def _get_continuous_pairs(self) -> list[list[Card]]:
        """获取所有可能的连对（3对及以上连续对子）"""
        results = []

        # 排除大小王
        normal_cards = [c for c in self.hand if not c.is_joker]
        if len(normal_cards) < 6:
            return results

        # 按点数分组，筛选出有对子的点数
        rank_counts = Counter(c.rank for c in normal_cards)
        pair_ranks = sorted([rank for rank, count in rank_counts.items() if count >= 2],
                           key=lambda r: r.value)

        if len(pair_ranks) < 3:
            return results

        # 尝试找连续的对子
        for start_idx in range(len(pair_ranks)):
            continuous_pairs = [pair_ranks[start_idx]]

            for i in range(start_idx + 1, len(pair_ranks)):
                prev_rank = continuous_pairs[-1]
                curr_rank = pair_ranks[i]

                if curr_rank.value - prev_rank.value == 1:
                    continuous_pairs.append(curr_rank)
                else:
                    break

                # 3对及以上生成组合
                if len(continuous_pairs) >= 3:
                    for length in range(3, len(continuous_pairs) + 1):
                        for start in range(len(continuous_pairs) - length + 1):
                            selected_ranks = continuous_pairs[start:start + length]
                            pair_cards = []
                            for rank in selected_ranks:
                                # 选取该点数的两张牌
                                for card in self.hand:
                                    if card.rank == rank and not card.is_joker:
                                        pair_cards.append(card)
                                        if len([c for c in pair_cards if c.rank == rank]) >= 2:
                                            break
                            if len(pair_cards) == length * 2:
                                results.append(pair_cards)

        return results

    def _get_triple_pairs(self) -> list[list[Card]]:
        """获取所有可能的三带二"""
        results = []

        # 按点数分组
        rank_groups: dict[Rank, list[Card]] = {}
        for card in self.hand:
            if not card.is_joker:
                if card.rank not in rank_groups:
                    rank_groups[card.rank] = []
                rank_groups[card.rank].append(card)

        # 找三张
        triple_ranks = [rank for rank, cards in rank_groups.items() if len(cards) >= 3]
        # 找对子
        pair_ranks = [rank for rank, cards in rank_groups.items() if len(cards) >= 2]

        for triple_rank in triple_ranks:
            triple_cards = rank_groups[triple_rank][:3]
            for pair_rank in pair_ranks:
                if pair_rank != triple_rank:
                    pair_cards = rank_groups[pair_rank][:2]
                    results.extend([triple_cards + pair_cards])

        return results

    def _get_airplanes(self) -> list[list[Card]]:
        """获取所有可能的飞机（两个及以上三张+对应数量的翅膀）"""
        results = []

        # 按点数分组
        rank_groups: dict[Rank, list[Card]] = {}
        for card in self.hand:
            if not card.is_joker:
                if card.rank not in rank_groups:
                    rank_groups[card.rank] = []
                rank_groups[card.rank].append(card)

        # 找三张及以上
        triple_ranks = sorted([rank for rank, cards in rank_groups.items() if len(cards) >= 3],
                             key=lambda r: r.value)

        if len(triple_ranks) < 2:
            return results

        # 找连续的三张
        for start_idx in range(len(triple_ranks)):
            continuous_triples = [triple_ranks[start_idx]]

            for i in range(start_idx + 1, len(triple_ranks)):
                prev_rank = continuous_triples[-1]
                curr_rank = triple_ranks[i]

                if curr_rank.value - prev_rank.value == 1:
                    continuous_triples.append(curr_rank)
                else:
                    break

            if len(continuous_triples) >= 2:
                # 需要翅膀
                # 找所有非三张的牌作为翅膀
                other_cards = []
                for rank, cards in rank_groups.items():
                    if rank not in continuous_triples:
                        other_cards.extend(cards[:1])  # 每种点数取一张作为翅膀候选

                # 生成飞机组合
                num_triples = len(continuous_triples)
                if len(other_cards) >= num_triples:
                    from itertools import combinations
                    for wings in combinations(other_cards, num_triples):
                        airplane_cards = []
                        for rank in continuous_triples:
                            airplane_cards.extend(rank_groups[rank][:3])
                        airplane_cards.extend(wings)
                        results.append(airplane_cards)

        return results

    def _get_steel_plates(self) -> list[list[Card]]:
        """获取所有可能的钢板（两个三张）"""
        results = []

        # 按点数分组
        rank_groups: dict[Rank, list[Card]] = {}
        for card in self.hand:
            if not card.is_joker:
                if card.rank not in rank_groups:
                    rank_groups[card.rank] = []
                rank_groups[card.rank].append(card)

        # 找三张及以上
        triple_ranks = sorted([rank for rank, cards in rank_groups.items() if len(cards) >= 3],
                             key=lambda r: r.value)

        if len(triple_ranks) < 2:
            return results

        # 找连续的三张
        for i in range(len(triple_ranks)):
            for j in range(i + 1, len(triple_ranks)):
                rank1 = triple_ranks[i]
                rank2 = triple_ranks[j]

                # 检查是否连续
                if rank2.value - rank1.value == 1:
                    steel_cards = []
                    steel_cards.extend(rank_groups[rank1][:3])
                    steel_cards.extend(rank_groups[rank2][:3])
                    results.append(steel_cards)

        return results

    def __repr__(self) -> str:
        return f"Player({self.player_id}, {self.name}, 位置:{self.position_name}, 手牌:{len(self.hand)}张)"
