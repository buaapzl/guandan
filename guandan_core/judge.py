"""
牌型判断和比较模块
"""
from collections import Counter
from typing import Optional

from guandan_core.cards import Card, CardType, Rank, Suit


def identify_card_type(cards: list[Card]) -> CardType:
    """
    识别一手牌的牌型

    牌型优先级：天王炸弹 > 炸弹 > 软炸弹 > 钢板 > 飞机 > 连对 > 顺子 > 三带二 > 三张 > 对子 > 单张
    """
    if not cards:
        return CardType.SINGLE

    # 按点数分组
    rank_counts = Counter(card.rank for card in cards)
    num_cards = len(cards)

    # 检查天王炸弹（4张王）
    if num_cards == 2:
        jokers = [card for card in cards if card.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)]
        if len(jokers) == 2:
            return CardType.KING_BOMB

    # 检查炸弹（4张及以上相同点数）
    max_rank_count = max(rank_counts.values()) if rank_counts else 0
    if max_rank_count >= 4:
        # 检查是否为软炸弹（含癞子）
        # 简化实现：暂时不处理癞子
        return CardType.BOMB

    # 检查钢板（两个三张333444）
    if num_cards >= 6:
        triples = [rank for rank, count in rank_counts.items() if count >= 3]
        if len(triples) >= 2:
            # 钢板是连续的三张
            sorted_triples = sorted(triples, key=lambda r: r.value)
            is_steel_plate = True
            for i in range(len(sorted_triples) - 1):
                if sorted_triples[i+1].value - sorted_triples[i].value != 1:
                    is_steel_plate = False
                    break
            if is_steel_plate:
                return CardType.STEEL_PLATE

    # 检查飞机（两个及以上三张+对应数量的翅膀）
    if num_cards >= 6:
        triples = [rank for rank, count in rank_counts.items() if count >= 3]
        if len(triples) >= 2:
            sorted_triples = sorted(triples, key=lambda r: r.value)
            # 检查是否连续
            is_airplane = True
            for i in range(len(sorted_triples) - 1):
                if sorted_triples[i+1].value - sorted_triples[i].value != 1:
                    is_airplane = False
                    break
            if is_airplane:
                return CardType.AIRPLANE

    # 检查连对（3对及以上连续对子）
    if num_cards >= 6:
        pairs = [rank for rank, count in rank_counts.items() if count >= 2]
        if len(pairs) >= 3:
            sorted_pairs = sorted(pairs, key=lambda r: r.value)
            is_continuous_pair = True
            for i in range(len(sorted_pairs) - 1):
                if sorted_pairs[i+1].value - sorted_pairs[i].value != 1:
                    is_continuous_pair = False
                    break
            if is_continuous_pair:
                return CardType.CONTINUOUS_PAIR

    # 检查顺子（5张及以上连续点数）
    if num_cards >= 5:
        # 排除大小王
        normal_ranks = [card.rank for card in cards
                       if card.rank not in (Rank.SMALL_JOKER, Rank.BIG_JOKER)]
        if len(set(normal_ranks)) == len(normal_ranks):  # 无重复
            sorted_ranks = sorted(normal_ranks, key=lambda r: r.value)
            # 检查是否连续（考虑A在K后循环）
            is_straight = True
            for i in range(len(sorted_ranks) - 1):
                if sorted_ranks[i+1].value - sorted_ranks[i].value != 1:
                    # 检查A-K循环
                    if not (sorted_ranks[i].value == 13 and sorted_ranks[i+1].value == 1):
                        is_straight = False
                        break
            if is_straight:
                return CardType.STRAIGHT

    # 检查三带二
    if num_cards == 5:
        triples = [rank for rank, count in rank_counts.items() if count == 3]
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(triples) == 1 and len(pairs) == 1:
            return CardType.TRIPLE_PAIR

    # 检查三张
    if num_cards == 3:
        if max_rank_count == 3:
            return CardType.TRIPLE

    # 检查对子
    if num_cards == 2:
        if max_rank_count == 2:
            return CardType.PAIR

    # 单张
    return CardType.SINGLE


def get_card_type_power(card_type: CardType, num_jokers: int = 0) -> int:
    """
    获取牌型基础强度
    """
    power_map = {
        CardType.SINGLE: 1,
        CardType.PAIR: 2,
        CardType.TRIPLE: 3,
        CardType.TRIPLE_PAIR: 4,
        CardType.STRAIGHT: 5,
        CardType.CONTINUOUS_PAIR: 6,
        CardType.AIRPLANE: 7,
        CardType.STEEL_PLATE: 8,
        CardType.BOMB: 9,
        CardType.SOFT_BOMB: 10,
        CardType.KING_BOMB: 11,
    }
    return power_map.get(card_type, 1)


def _get_main_rank(cards: list[Card]) -> Optional[Rank]:
    """
    获取一手牌的主点数（用于比较大小）
    """
    rank_counts = Counter(card.rank for card in cards)

    # 炸弹：返回相同点数
    if len(cards) == 4:
        for rank, count in rank_counts.items():
            if count == 4:
                return rank

    # 天王炸弹
    if len(cards) == 2:
        jokers = [card for card in cards if card.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)]
        if len(jokers) == 2:
            return Rank.BIG_JOKER

    # 三张
    for rank, count in rank_counts.items():
        if count == 3:
            return rank

    # 对子
    for rank, count in rank_counts.items():
        if count == 2:
            return rank

    # 单张：返回最大的那张
    normal_cards = [c for c in cards if c.rank not in (Rank.SMALL_JOKER, Rank.BIG_JOKER)]
    if normal_cards:
        return min(normal_cards, key=lambda c: c.rank.value).rank

    # 如果只有王
    jokers = [c for c in cards if c.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)]
    if jokers:
        return max(jokers, key=lambda c: c.rank.value).rank

    return None


def compare_card_types(cards1: list[Card], cards2: list[Card]) -> int:
    """
    比较两组牌的大小
    返回: 1=cards1大, -1=cards2大, 0=相等
    """
    if not cards1 or not cards2:
        return 0

    type1 = identify_card_type(cards1)
    type2 = identify_card_type(cards2)

    power1 = get_card_type_power(type1)
    power2 = get_card_type_power(type2)

    # 牌型不同，按牌型优先级比较
    if power1 != power2:
        return 1 if power1 > power2 else -1

    # 牌型相同，按主点数比较
    rank1 = _get_main_rank(cards1)
    rank2 = _get_main_rank(cards2)

    if rank1 is None or rank2 is None:
        return 0

    # 点数比较：A最大（值为1），2最小（值为13）
    # 所以值越小，点数越大
    if rank1.value < rank2.value:
        return 1
    elif rank1.value > rank2.value:
        return -1

    return 0
