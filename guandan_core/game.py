"""
掼蛋游戏主逻辑模块
"""
import random
from typing import Optional

from guandan_core.cards import Card, Rank, Suit, create_deck


def create_double_deck() -> list[Card]:
    """
    创建两副牌（108张），掼蛋使用
    """
    deck = []
    # 普通牌点数: 3,4,5,6,7,8,9,10,J,Q,K,A,2 (共13种)
    normal_ranks = [
        Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
        Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.J, Rank.Q,
        Rank.K, Rank.A, Rank.TWO
    ]
    # 两副普通牌: 52 * 2 = 104张
    for _ in range(2):
        for rank in normal_ranks:
            for suit in range(Suit.SPADE, Suit.DIAMOND + 1):
                deck.append(Card(rank, Suit(suit)))
    # 大小王各2张: 4张
    deck.append(Card(Rank.SMALL_JOKER, None))
    deck.append(Card(Rank.SMALL_JOKER, None))
    deck.append(Card(Rank.BIG_JOKER, None))
    deck.append(Card(Rank.BIG_JOKER, None))
    return deck
from guandan_core.player import Player
from guandan_core.team import Team
from guandan_core.recorder import Recorder
from guandan_core.rule_config import RuleConfig
from guandan_core.judge import identify_card_type, compare_card_types


class GuandanGame:
    """掼蛋游戏主逻辑"""

    def __init__(self, config: Optional[RuleConfig] = None):
        """
        初始化游戏

        Args:
            config: 规则配置，默认使用标准规则
        """
        self.config = config or RuleConfig.standard()

        # 创建4个玩家，位置对应：0=南, 1=西, 2=北, 3=东
        self.players: list[Player] = [
            Player(0, f"玩家{0}"),
            Player(1, f"玩家{1}"),
            Player(2, f"玩家{2}"),
            Player(3, f"玩家{3}"),
        ]

        # 创建2个队伍
        # 队伍0：0和2是一家（南和北）
        # 队伍1：1和3是一家（西和东）
        self.teams: list[Team] = [Team(0), Team(1)]

        # 绑定玩家到队伍
        self.teams[0].add_player(self.players[0])
        self.teams[0].add_player(self.players[2])
        self.teams[1].add_player(self.players[1])
        self.teams[1].add_player(self.players[3])

        # 初始化记牌器
        self.recorder = Recorder()

        # 游戏状态
        self.current_player: int = 0  # 当前出牌玩家
        self.round: int = 1            # 当前回合
        self.base_level: int = 2       # 基础等级

        # 当前回合的出牌记录
        self.current_play: list[list[Card]] = []  # 每位玩家的出牌
        self.first_player: int = 0    # 本轮首家

        # 底牌
        self.bottom_cards: list[Card] = []

    def shuffle_and_deal(self, seed: Optional[int] = None):
        """
        洗牌发牌

        Args:
            seed: 随机种子，用于复现
        """
        if seed is not None:
            random.seed(seed)

        # 创建两副牌（108张）
        deck = create_double_deck()

        # 洗牌
        random.shuffle(deck)

        # 发牌：每人27张，留3张底牌
        cards_per_player = 27
        for i in range(4):
            player_cards = deck[i * cards_per_player:(i + 1) * cards_per_player]
            self.players[i].receive_cards(player_cards)

        # 留底牌
        self.bottom_cards = deck[4 * cards_per_player:]

        # 重置记牌器
        self.recorder.reset()

    def deal_cards(self):
        """
        发牌（简化版，默认使用随机种子0）
        """
        self.shuffle_and_deal(seed=0)

    def get_legal_actions(self, player_id: int) -> list[list[Card]]:
        """
        获取当前玩家的合法出牌

        Args:
            player_id: 玩家ID

        Returns:
            合法的出牌列表
        """
        player = self.players[player_id]
        if player.is_empty:
            return []

        # 首家可以出任意牌
        if self.first_player == player_id:
            return player.get_playable_cards()

        # 后续玩家必须大过上家或用炸弹
        if not self.current_play:
            # 如果当前没有出牌，可以出任意牌
            return player.get_playable_cards()

        # 获取上家的出牌
        last_play = self.current_play[-1]
        if last_play is None:
            # 上家pass了，可以出任意牌
            return player.get_playable_cards()

        # 获取所有可出的牌
        all_playable = player.get_playable_cards()

        # 过滤出能大过上家的牌
        legal_actions = []
        for cards in all_playable:
            result = compare_card_types(cards, last_play)
            if result > 0:  # 当前牌大于上家
                legal_actions.append(cards)

        return legal_actions

    def play_cards(self, player_id: int, cards: list[Card]) -> bool:
        """
        玩家出牌

        Args:
            player_id: 玩家ID
            cards: 要出的牌

        Returns:
            是否出牌成功
        """
        player = self.players[player_id]

        # 验证玩家是否轮到你
        if player_id != self.current_player:
            return False

        # 验证玩家是否有这些牌
        if not player.remove_cards(cards):
            return False

        # 记录出牌
        if len(self.current_play) <= player_id:
            self.current_play.extend([None] * (player_id - len(self.current_play) + 1))
        self.current_play[player_id] = cards

        # 记录到记牌器
        self.recorder.record(cards)

        # 如果是首家，记录
        if self.first_player is None:
            self.first_player = player_id

        # 检查是否一轮结束（所有玩家都出过牌或pass）
        self._check_round_end()

        # 切换到下一个玩家
        self._next_player()

        return True

    def _next_player(self):
        """切换到下一个玩家"""
        self.current_player = (self.current_player + 1) % 4

    def _check_round_end(self):
        """检查一轮是否结束"""
        # 检查是否所有玩家都出过牌
        if len(self.current_play) < 4:
            return

        # 检查是否所有非空出牌都已完成
        non_empty_count = sum(1 for play in self.current_play if play is not None)
        if non_empty_count >= 4:
            # 一轮结束，找到本轮获胜者
            winner_id = self._get_round_winner()
            self._on_round_end(winner_id)

    def _get_round_winner(self) -> int:
        """获取本轮获胜者"""
        if not self.current_play or self.first_player is None:
            return self.current_player

        # 找到最大的牌
        winner_id = self.first_player
        winner_cards = self.current_play[self.first_player]

        for i, cards in enumerate(self.current_play):
            if cards is None:
                continue
            if compare_card_types(cards, winner_cards) > 0:
                winner_cards = cards
                winner_id = i

        return winner_id

    def _on_round_end(self, winner_id: int):
        """
        一轮结束

        Args:
            winner_id: 本轮获胜者ID
        """
        # 重置当前出牌记录
        self.current_play = []
        self.first_player = None

        # 设置下一轮的首家
        self.current_player = winner_id

        # 检查是否有人赢了这一局（手牌为空）
        for i, player in enumerate(self.players):
            if player.is_empty:
                # 可以在这里处理玩家获胜的逻辑
                pass

    def reset(self, seed: Optional[int] = None):
        """
        重置游戏

        Args:
            seed: 随机种子
        """
        # 清理玩家手牌
        for player in self.players:
            player.hand.clear()

        # 重置队伍
        for team in self.teams:
            team.level = self.base_level
            team.wins = 0

        # 重置记牌器
        self.recorder.reset()

        # 重置游戏状态
        self.current_player = 0
        self.round = 1
        self.current_play = []
        self.first_player = None
        self.bottom_cards = []

        # 重新发牌
        self.shuffle_and_deal(seed)
