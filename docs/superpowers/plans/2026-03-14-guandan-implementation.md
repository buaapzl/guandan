# 掼蛋游戏RL训练平台实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的掼蛋游戏平台，支持RL训练和PyGame人机对战

**Architecture:** 分层架构 - 核心引擎(guandan_core) → RL环境(guandan_gym) → UI(guandan_ui) → 训练(trainer)

**Tech Stack:** Python, Gymnasium, Stable-Baselines3, PyGame

---

## 文件结构

```
guandan/
├── guandan_core/
│   ├── __init__.py
│   ├── cards.py          # 扑克牌定义（Card, CardType, Suit, Rank）
│   ├── player.py         # 玩家类（Player）
│   ├── team.py          # 队伍信息管理（Team）
│   ├── game.py          # 游戏主逻辑（GuandanGame）
│   ├── judge.py         # 牌型判断（CardType, compare_cards）
│   ├── recorder.py      # 记牌器（Recorder）
│   ├── calculator.py    # 算牌器（Calculator）
│   └── rule_config.py   # 规则配置（RuleConfig）
│
├── guandan_gym/
│   ├── __init__.py
│   ├── env.py           # Gymnasium环境（GuandanEnv）
│   ├── obs_space.py     # 观察空间
│   └── action_space.py  # 动作空间
│
├── guandan_ui/
│   ├── __init__.py
│   ├── main.py          # 游戏主界面
│   ├── renderer.py      # 渲染器
│   └── controller.py    # 输入控制
│
├── trainer/
│   ├── __init__.py
│   ├── train.py         # 训练入口
│   └── config.py         # 训练配置
│
├── tests/
│   ├── __init__.py
│   ├── test_cards.py
│   ├── test_judge.py
│   ├── test_game.py
│   └── test_gym.py
│
├── pyproject.toml
└── README.md
```

---

## Chunk 1: 核心游戏引擎 (guandan_core)

### Task 1: 牌型定义 (cards.py)

**Files:**
- Create: `guandan_core/__init__.py`
- Create: `guandan_core/cards.py`
- Test: `tests/test_cards.py`

- [ ] **Step 1: 创建 tests/test_cards.py**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cards.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Write implementation**

创建 `guandan_core/__init__.py`:
```python
from .cards import Card, CardType, Suit, Rank
from .player import Player
from .team import Team
from .game import GuandanGame
from .judge import CardType, compare_cards
from .recorder import Recorder
from .calculator import Calculator
from .rule_config import RuleConfig

__all__ = [
    'Card', 'CardType', 'Suit', 'Rank',
    'Player', 'Team', 'GuandanGame',
    'CardType', 'compare_cards',
    'Recorder', 'Calculator', 'RuleConfig',
]
```

创建 `guandan_core/cards.py`:
```python
from enum import Enum
from typing import Optional

class Suit(Enum):
    SPADE = 1    # 黑桃
    HEART = 2    # 红桃
    CLUB = 3     # 梅花
    DIAMOND = 4  # 方片
    JOKER = 5    # 王（无花色）

class Rank(Enum):
    SMALL_JOKER = 0   # 小王
    BIG_JOKER = 1     # 大王
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7
    NINE = 8
    TEN = 9
    J = 10
    Q = 11
    K = 12
    A = 13
    TWO = 14

class CardType(Enum):
    SINGLE = "single"           # 单张
    PAIR = "pair"               # 对子
    TRIPLE = "triple"           # 三张
    TRIPLE_PAIR = "triple_pair" # 三带二
    STRAIGHT = "straight"       # 顺子
    CONTINUOUS_PAIR = "continuous_pair"  # 连对
    AIRPLANE = "airplane"       # 飞机
    STEEL_PLATE = "steel_plate"  # 钢板
    BOMB = "bomb"               # 炸弹
    SOFT_BOMB = "soft_bomb"     # 软炸弹
    KING_BOMB = "king_bomb"     # 天王炸弹

class Card:
    def __init__(self, rank: Rank, suit: Optional[Suit]):
        self.rank = rank
        self.suit = suit

    @property
    def is_joker(self) -> bool:
        return self.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)

    def to_index(self) -> int:
        """转换为0-53的索引"""
        if self.rank == Rank.SMALL_JOKER:
            return 52
        elif self.rank == Rank.BIG_JOKER:
            return 53
        else:
            return (self.rank.value - 2) * 4 + self.suit.value - 1

    @classmethod
    def from_index(cls, index: int) -> 'Card':
        """从索引创建牌"""
        if index == 52:
            return cls(Rank.SMALL_JOKER, None)
        elif index == 53:
            return cls(Rank.BIG_JOKER, None)
        else:
            rank = Rank(index // 4 + 2)
            suit = Suit(index % 4 + 1)
            return cls(rank, suit)

    def __repr__(self):
        if self.is_joker:
            return f"{'小王' if self.rank == Rank.SMALL_JOKER else '大王'}"
        suit_name = {Suit.SPADE: '♠', Suit.HEART: '♥', Suit.CLUB: '♣', Suit.DIAMOND: '♦'}
        rank_name = {Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5', Rank.SIX: '6',
                     Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9', Rank.TEN: '10',
                     Rank.J: 'J', Rank.Q: 'Q', Rank.K: 'K', Rank.A: 'A', Rank.TWO: '2'}
        return f"{rank_name[self.rank]}{suit_name.get(self.suit, '')}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def __lt__(self, other):
        return self.rank.value < other.rank.value

    def __gt__(self, other):
        return self.rank.value > other.rank.value

    def __le__(self, other):
        return self <= other

    def __ge__(self, other):
        return self >= other

def create_deck() -> list[Card]:
    """创建一副牌"""
    deck = []
    # 普通牌
    for rank in range(Rank.THREE.value, Rank.TWO.value + 1):
        for suit in Suit:
            if suit != Suit.JOKER:
                deck.append(Card(Rank(rank), suit))
    # 大小王
    deck.append(Card(Rank.SMALL_JOKER, None))
    deck.append(Card(Rank.BIG_JOKER, None))
    return deck
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cards.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add guandan_core/__init__.py guandan_core/cards.py tests/test_cards.py
git commit -m "feat: add card definitions and utilities"
```

---

### Task 2: 牌型判断 (judge.py)

**Files:**
- Create: `guandan_core/judge.py`
- Test: `tests/test_judge.py`

- [ ] **Step 1: Write tests/test_judge.py**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_judge.py -v`
Expected: FAIL

- [ ] **Step 3: Write guandan_core/judge.py**

```python
from typing import Optional
from collections import Counter
from guandan_core.cards import Card, CardType, Rank

def identify_card_type(cards: list[Card]) -> Optional[CardType]:
    """识别牌型"""
    if not cards:
        return None

    n = len(cards)
    ranks = [c.rank for c in cards]
    rank_counts = Counter(ranks)
    is_joker_in_cards = any(c.is_joker for c in cards)

    # 天王炸弹
    if n == 2 and is_joker_in_cards and len(rank_counts) == 2:
        return CardType.KING_BOMB

    # 炸弹（4张及以上相同点数）
    if max(rank_counts.values()) >= 4:
        return CardType.SOFT_BOMB if is_joker_in_cards else CardType.BOMB

    # 钢板（两个三张）
    triple_ranks = [r for r, c in rank_counts.items() if c == 3]
    if len(triple_ranks) >= 2:
        return CardType.STEEL_PLATE

    # 飞机（三带翅膀）
    if 3 in rank_counts.values():
        # 简化实现
        return CardType.AIRPLANE

    # 连对（3对及以上）
    if len(rank_counts) >= 3:
        sorted_ranks = sorted([r.value for r in rank_counts.keys()])
        is_continuous = all(sorted_ranks[i] + 1 == sorted_ranks[i+1] for i in range(len(sorted_ranks)-1))
        if is_continuous:
            return CardType.CONTINUOUS_PAIR

    # 顺子（5张及以上）
    if n >= 5 and len(rank_counts) == n:
        sorted_ranks = sorted([r.value for r in rank_counts.keys()])
        # A可以循环到2
        if 2 not in [r.value for r in rank_counts.keys()]:  # 2不能参与顺子
            return CardType.STRAIGHT

    # 三带二
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return CardType.TRIPLE_PAIR

    # 三张
    if 3 in rank_counts.values():
        return CardType.TRIPLE

    # 对子
    if 2 in rank_counts.values():
        return CardType.PAIR

    # 单张
    return CardType.SINGLE

def get_card_type_power(card_type: CardType, num_jokers: int = 0) -> int:
    """获取牌型基础强度"""
    powers = {
        CardType.SINGLE: 1,
        CardType.PAIR: 2,
        CardType.TRIPLE: 3,
        CardType.TRIPLE_PAIR: 4,
        CardType.STRAIGHT: 5,
        CardType.CONTINUOUS_PAIR: 6,
        CardType.AIRPLANE: 7,
        CardType.STEEL_PLATE: 8,
        CardType.SOFT_BOMB: 9,
        CardType.BOMB: 10,
        CardType.KING_BOMB: 11,
    }
    return powers.get(card_type, 0)

def compare_card_types(cards1: list[Card], cards2: list[Card]) -> int:
    """比较两组牌的大小
    返回: 1=cards1大, -1=cards2大, 0=相等"""
    type1 = identify_card_type(cards1)
    type2 = identify_card_type(cards2)

    if type1 != type2:
        # 炸弹可以压任意牌型
        if type1 in (CardType.BOMB, CardType.SOFT_BOMB, CardType.KING_BOMB):
            return 1
        if type2 in (CardType.BOMB, CardType.SOFT_BOMB, CardType.KING_BOMB):
            return -1

        # 比较牌型强度
        return 1 if get_card_type_power(type1) > get_card_type_power(type2) else -1

    # 同牌型比较
    ranks1 = [c.rank for c in cards1]
    ranks2 = [c.rank for c in cards2]

    # 天王炸弹相同
    if type1 == CardType.KING_BOMB:
        return 0

    # 按主牌点数比较
    def get_main_rank(ranks):
        c = Counter(ranks)
        return max(c.keys(), key=lambda r: c[r] * 100 + r.value)

    main1 = get_main_rank(ranks1)
    main2 = get_main_rank(ranks2)

    return 1 if main1.value > main2.value else (-1 if main1.value < main2.value else 0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_judge.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add guandan_core/judge.py tests/test_judge.py
git commit -m "feat: add card type identification and comparison"
```

---

### Task 3: 玩家与队伍 (player.py, team.py)

**Files:**
- Create: `guandan_core/player.py`
- Create: `guandan_core/team.py`

- [ ] **Step 1: Write guandan_core/player.py**

```python
from typing import Optional
from guandan_core.cards import Card

class Player:
    def __init__(self, player_id: int, name: str = ""):
        self.player_id = player_id
        self.name = name or f"Player{player_id}"
        self.hand: list[Card] = []
        self.position: int = player_id  # 0=南, 1=西, 2=北, 3=东

    @property
    def is_empty(self) -> bool:
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
        """获取所有可出的牌型组合"""
        from guandan_core.judge import identify_card_type
        from collections import Counter

        playable = []
        n = len(self.hand)

        # 单张
        for c in self.hand:
            playable.append([c])

        # 对子
        ranks = Counter(c.rank for c in self.hand)
        for r, cnt in ranks.items():
            if cnt >= 2:
                pair = [c for c in self.hand if c.rank == r][:2]
                playable.append(pair)

        # 三张及以上
        for r, cnt in ranks.items():
            if cnt >= 3:
                triple = [c for c in self.hand if c.rank == r][:cnt]
                playable.append(triple)

        # 炸弹（简化）
        if ranks:
            max_cnt = max(ranks.values())
            if max_cnt >= 4:
                for r, cnt in ranks.items():
                    if cnt >= 4:
                        bomb = [c for c in self.hand if c.rank == r][:cnt]
                        playable.append(bomb)

        return playable

    def __repr__(self):
        return f"{self.name}: {self.hand}"
```

- [ ] **Step 2: Write guandan_core/team.py**

```python
from guandan_core.player import Player

class Team:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.players: list[Player] = []
        self.level: int = 2  # 当前等级
        self.wins: int = 0   # 获胜次数

    def add_player(self, player: Player):
        self.players.append(player)

    def is_complete(self) -> bool:
        return len(self.players) == 2

    def get_teammate(self, player: Player) -> Player:
        """获取队友"""
        for p in self.players:
            if p != player:
                return p

    def has_first_place(self) -> bool:
        """是否有头游"""
        return any(p.is_empty for p in self.players)

    def __repr__(self):
        return f"Team{self.team_id}(L{self.level}, wins={self.wins})"
```

- [ ] **Step 3: Commit**

```bash
git add guandan_core/player.py guandan_core/team.py
git commit -m "feat: add player and team classes"
```

---

### Task 4: 记牌器与算牌器 (recorder.py, calculator.py)

**Files:**
- Create: `guandan_core/recorder.py`
- Create: `guandan_core/calculator.py`

- [ ] **Step 1: Write guandan_core/recorder.py**

```python
from collections import Counter
from guandan_core.cards import Card, Rank

class Recorder:
    """记牌器：跟踪已打出的牌"""

    def __init__(self):
        self.played_cards: list[Card] = []
        self.played_ranks = Counter()  # 各点数已打出的数量

    def record(self, cards: list[Card]):
        """记录已打出的牌"""
        self.played_cards.extend(cards)
        for c in cards:
            self.played_ranks[c.rank] += 1

    def get_remaining(self, rank: Rank) -> int:
        """获取某点数的剩余数量"""
        base = 4 if rank not in (Rank.SMALL_JOKER, Rank.BIG_JOKER) else 1
        return base - self.played_ranks.get(rank, 0)

    def is_exhausted(self, rank: Rank) -> bool:
        """某点数是否已打完"""
        return self.get_remaining(rank) == 0

    def get_remaining_cards(self) -> dict[Rank, int]:
        """获取所有剩余牌统计"""
        result = {}
        for rank in Rank:
            remaining = self.get_remaining(rank)
            if remaining > 0:
                result[rank] = remaining
        return result

    def reset(self):
        """重置"""
        self.played_cards.clear()
        self.played_ranks.clear()
```

- [ ] **Step 2: Write guandan_core/calculator.py**

```python
from guandan_core.recorder import Recorder
from guandan_core.cards import Rank

class Calculator:
    """算牌器：根据已知信息估算概率"""

    def __init__(self, recorder: Recorder, my_hand_ranks: set[Rank]):
        self.recorder = recorder
        self.my_hand_ranks = my_hand_ranks

    def get_opponent_presence_prob(self, rank: Rank) -> float:
        """估算对手持有某点数的概率"""
        remaining = self.recorder.get_remaining(rank)
        if remaining <= 0:
            return 0.0

        # 假设3个对手，简化计算
        # 排除自己手中的牌
        in_my_hand = 1 if rank in self.my_hand_ranks else 0
        remaining_for_opponents = remaining - in_my_hand

        if remaining_for_opponents <= 0:
            return 0.0

        # 每个对手平均持有的数量
        avg_per_opponent = remaining_for_opponents / 3
        return min(1.0, avg_per_opponent / 4)  # 最多4张

    def get_dangerous_ranks(self, threshold: float = 0.5) -> list[Rank]:
        """获取危险的点数（对手很可能有）"""
        dangerous = []
        for rank in Rank:
            prob = self.get_opponent_presence_prob(rank)
            if prob >= threshold:
                dangerous.append(rank)
        return dangerous

    def suggest_play(self, playable_combos: list) -> list:
        """建议出牌（简化版）"""
        # 优先出危险牌
        dangerous = set(self.get_dangerous_ranks())

        scored = []
        for combo in playable_combos:
            if combo:
                main_rank = combo[0].rank
                if main_rank in dangerous:
                    score = 10  # 高优先级
                else:
                    score = 1
                scored.append((score, combo))

        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored]
```

- [ ] **Step 3: Commit**

```bash
git add guandan_core/recorder.py guandan_core/calculator.py
git commit -m "feat: add recorder and calculator"
```

---

### Task 5: 规则配置 (rule_config.py)

**Files:**
- Create: `guandan_core/rule_config.py`

- [ ] **Step 1: Write guandan_core/rule_config.py**

```python
from dataclasses import dataclass

@dataclass
class RuleConfig:
    # 基础规则
    use_joker: bool = True           # 是否使用癞子
    joker_can_be_bomb: bool = False  # 癞子能否配成炸弹

    # 贡牌规则
    use_sacrifice: bool = True       # 是否使用贡牌
    can_resist_ace: bool = True      # 能否抗贡（A/K）
    return_card: bool = True         # 是否还贡

    # 升级规则
    first_level_up: int = 2          # 头游冲几
    protect_level: int = 2           # 二游保几

    # 炸弹升级
    bomb_upgrade: bool = True        # 炸弹是否升级
    bomb_upgrade_level: int = 2      # 炸弹升级几级

    @classmethod
    def standard(cls) -> 'RuleConfig':
        """标准规则"""
        return cls()

    @classmethod
    def simple(cls) -> 'RuleConfig':
        """简化规则（无贡牌）"""
        return cls(
            use_sacrifice=False,
            bomb_upgrade=False,
        )
```

- [ ] **Step 2: Commit**

```bash
git add guandan_core/rule_config.py
git commit -m "feat: add rule configuration"
```

---

### Task 6: 游戏主逻辑 (game.py)

**Files:**
- Create: `guandan_core/game.py`
- Test: `tests/test_game.py`

- [ ] **Step 1: Write tests/test_game.py**

```python
import pytest
from guandan_core.game import GuandanGame
from guandan_core.cards import Card, Rank, Suit

def test_game_initialization():
    game = GuandanGame()
    assert game.current_player == 0
    assert game.round == 1

def test_deal_cards():
    game = GuandanGame()
    game.deal_cards()
    # 每人应该发27张牌（去掉3张底牌 = 51张，4人）
    for i in range(4):
        assert len(game.players[i].hand) == 27

def test_get_legal_actions():
    game = GuandanGame()
    game.deal_cards()
    actions = game.get_legal_actions(0)
    assert len(actions) > 0

def test_play_cards():
    game = GuandanGame()
    game.deal_cards()
    # 首家可以出任意牌
    player = game.players[0]
    # 取第一手合法牌
    actions = game.get_legal_actions(0)
    if actions:
        game.play_cards(0, actions[0])
        assert len(player.hand) < 27
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_game.py -v`
Expected: FAIL

- [ ] **Step 3: Write guandan_core/game.py**

```python
import random
from typing import Optional
from guandan_core.cards import Card, create_deck, Rank
from guandan_core.player import Player
from guandan_core.team import Team
from guandan_core.recorder import Recorder
from guandan_core.rule_config import RuleConfig

class GuandanGame:
    """掼蛋游戏主逻辑"""

    def __init__(self, config: Optional[RuleConfig] = None):
        self.config = config or RuleConfig.standard()
        self.players = [Player(i) for i in range(4)]
        self.teams = [Team(0), Team(1)]

        # 组队
        self.teams[0].add_player(self.players[0])  # 南-北是一家
        self.teams[0].add_player(self.players[2])
        self.teams[1].add_player(self.players[1])  # 西-东是一家
        self.teams[1].add_player(self.players[3])

        self.recorder = Recorder()
        self.current_player = 0  # 当前出牌玩家
        self.last_play = None    # 上家出的牌
        self.last_player = None  # 上家出牌玩家
        self.round = 1           # 回合
        self.level = 2           # 当前等级
        self.deck: list[Card] = []
        self.bottom_cards: list[Card] = []  # 底牌
        self.winner: Optional[int] = None
        self.game_over = False

    def shuffle_and_deal(self, seed: Optional[int] = None):
        """洗牌发牌"""
        if seed is not None:
            random.seed(seed)

        self.deck = create_deck()
        random.shuffle(self.deck)

        # 发牌（每人27张，留3张底牌）
        for i in range(4):
            self.players[i].hand = self.deck[i*27:(i+1)*27]
            self.players[i].hand.sort()

        self.bottom_cards = self.deck[-3:]

    def deal_cards(self):
        """发牌（简化版）"""
        self.shuffle_and_deal()

    def get_legal_actions(self, player_id: int) -> list[list[Card]]:
        """获取当前玩家的合法出牌"""
        player = self.players[player_id]

        if self.last_player is None:
            # 首家可以出任意牌
            return player.get_playable_cards()

        # 必须大过上家
        from guandan_core.judge import compare_card_types
        playable = []
        for combo in player.get_playable_cards():
            if compare_card_types(combo, self.last_play) > 0:
                playable.append(combo)

        # 也可以用炸弹
        # （简化：炸弹已在get_playable_cards中包含）
        return playable

    def play_cards(self, player_id: int, cards: list[Card]) -> bool:
        """玩家出牌"""
        player = self.players[player_id]

        # 验证合法性
        if self.last_player is not None:
            from guandan_core.judge import compare_card_types
            if compare_card_types(cards, self.last_play) <= 0:
                return False

        # 出牌
        if player.remove_cards(cards):
            self.recorder.record(cards)
            self.last_play = cards
            self.last_player = player_id

            # 检查是否赢了这一轮
            if player.is_empty:
                self._on_round_end(player_id)

            # 下一家
            self.current_player = (player_id + 1) % 4
            return True

        return False

    def _on_round_end(self, winner_id: int):
        """一轮结束"""
        # 更新队伍状态
        team_id = winner_id % 2
        self.teams[team_id].wins += 1

        # 检查是否整局结束
        if all(p.is_empty for p in self.players):
            self.game_over = True
            self.winner = team_id

    def reset(self, seed: Optional[int] = None):
        """重置游戏"""
        self.__init__(self.config)
        self.deal_cards()

    def __repr__(self):
        return f"GuandanGame(round={self.round}, level={self.level}, current={self.current_player})"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_game.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add guandan_core/game.py tests/test_game.py
git commit -m "feat: add main game logic"
```

---

## Chunk 2: Gymnasium RL环境 (guandan_gym)

### Task 7: Gymnasium环境实现

**Files:**
- Create: `guandan_gym/__init__.py`
- Create: `guandan_gym/env.py`
- Create: `tests/test_gym.py`

- [ ] **Step 1: Write guandan_gym/__init__.py**

```python
from guandan_gym.env import GuandanEnv

__all__ = ['GuandanEnv']
```

- [ ] **Step 2: Write guandan_gym/env.py**

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any

class GuandanEnv(gym.Env):
    """掼蛋Gymnasium环境"""

    metadata = {'render_modes': ['human']}

    def __init__(self, render_mode: Optional[str] = None):
        super().__init__()

        self.render_mode = render_mode
        self.game = None
        self._init_game()

        # 观察空间：54张牌的各种特征
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(280,), dtype=np.float32
        )

        # 动作空间：离散空间
        self.action_space = spaces.Discrete(2000)

    def _init_game(self):
        from guandan_core.game import GuandanGame
        self.game = GuandanGame()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, dict]:
        """重置环境"""
        self._init_game()
        self.game.deal_cards()

        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """执行动作"""
        # 将动作转换为具体出牌
        playable = self.game.get_legal_actions(self.game.current_player)

        if action < len(playable):
            cards = playable[action]
            self.game.play_cards(self.game.current_player, cards)

        obs = self._get_observation()
        reward = self._compute_reward()
        terminated = self.game.game_over
        truncated = False
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        obs = np.zeros(280, dtype=np.float32)

        player = self.game.players[self.game.current_player]

        # 手牌（0-53）
        for card in player.hand:
            obs[card.to_index()] = 1.0

        # 已打出的牌（54-107）
        if self.game.recorder.played_cards:
            for card in self.game.recorder.played_cards:
                obs[54 + card.to_index()] = 1.0

        # 上家出牌（108-161）
        if self.game.last_play:
            for card in self.game.last_play:
                obs[108 + card.to_index()] = 1.0

        # 游戏状态（162-165）
        obs[162 + self.game.current_player] = 1.0

        # 等级信息（166-169）
        obs[166 + self.game.level - 2] = 1.0

        return obs

    def _compute_reward(self) -> float:
        """计算奖励"""
        if self.game.game_over:
            if self.game.winner == self.game.current_player % 2:
                return 1.0
            else:
                return -1.0
        return 0.0

    def _get_info(self) -> dict:
        """获取额外信息"""
        return {
            'current_player': self.game.current_player,
            'hand_size': len(self.game.players[self.game.current_player].hand),
            'round': self.game.round,
        }

    def legal_actions_mask(self) -> np.ndarray:
        """获取合法动作掩码"""
        mask = np.zeros(self.action_space.n, dtype=np.int8)
        playable = self.game.get_legal_actions(self.game.current_player)
        for i in range(min(len(playable), self.action_space.n)):
            mask[i] = 1
        return mask

    def render(self):
        if self.render_mode == 'human':
            print(self.game)

    def close(self):
        pass
```

- [ ] **Step 3: Write tests/test_gym.py**

```python
import pytest
import numpy as np
from guandan_gym.env import GuandanEnv

def test_env_creation():
    env = GuandanEnv()
    assert env.observation_space.shape == (280,)
    assert env.action_space.n == 2000

def test_env_reset():
    env = GuandanEnv()
    obs, info = env.reset()
    assert obs.shape == (280,)
    assert 'current_player' in info

def test_env_step():
    env = GuandanEnv()
    env.reset()

    mask = env.legal_actions_mask()
    legal_actions = np.where(mask)[0]

    if len(legal_actions) > 0:
        action = legal_actions[0]
        obs, reward, terminated, truncated, info = env.step(action)
        assert obs.shape == (280,)
        assert isinstance(reward, float)

def test_legal_actions():
    env = GuandanEnv()
    env.reset()

    mask = env.legal_actions_mask()
    assert mask.sum() > 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gym.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add guandan_gym/ tests/test_gym.py
git commit -m "feat: add gymnasium environment"
```

---

## Chunk 3: PyGame UI (guandan_ui)

### Task 8: PyGame UI实现

**Files:**
- Create: `guandan_ui/__init__.py`
- Create: `guandan_ui/main.py`
- Create: `guandan_ui/renderer.py`

- [ ] **Step 1: Write guandan_ui/__init__.py**

```python
from guandan_ui.main import GuandanUI

__all__ = ['GuandanUI']
```

- [ ] **Step 2: Write guandan_ui/main.py**

```python
import pygame
from guandan_core.game import GuandanGame
from guandan_core.cards import Card

class GuandanUI:
    """PyGame UI主类"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("掼蛋游戏")

        self.game = GuandanGame()
        self.game.deal_cards()

        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_cards: list[Card] = []

    def run(self):
        """主循环"""
        while self.running:
            self._handle_events()
            self._render()
            self.clock.tick(30)

        pygame.quit()

    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse(event.pos, event.button)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._play_cards()
                elif event.key == pygame.K_h:
                    self._hint()

    def _handle_mouse(self, pos, button):
        """处理鼠标点击"""
        # 简化：点击选牌
        player = self.game.players[0]
        card_width = 80
        start_x = 600 - (len(player.hand) * card_width) // 2

        for i, card in enumerate(player.hand):
            x = start_x + i * card_width
            y = 650
            if x <= pos[0] <= x + card_width and y <= pos[1] <= y + 120:
                if button == 1:  # 左键选中
                    if card in self.selected_cards:
                        self.selected_cards.remove(card)
                    else:
                        self.selected_cards.append(card)
                elif button == 3:  # 右键取消
                    self.selected_cards.clear()
                break

    def _play_cards(self):
        """出牌"""
        if not self.selected_cards:
            return

        if self.game.play_cards(0, self.selected_cards):
            self.selected_cards.clear()

    def _hint(self):
        """提示"""
        from guandan_core.calculator import Calculator
        from guandan_core.cards import Rank

        player = self.game.players[0]
        my_ranks = set(c.rank for c in player.hand)
        calc = Calculator(self.game.recorder, my_ranks)

        playable = self.game.get_legal_actions(0)
        suggestions = calc.suggest_play(playable)

        if suggestions:
            self.selected_cards = suggestions[0]

    def _render(self):
        """渲染"""
        self.screen.fill((34, 139, 34))  # 绿色牌桌

        # 渲染四家手牌（简化）
        self._render_player(0, (600, 700))  # 己方
        self._render_player(2, (600, 50))   # 对家
        self._render_player(1, (50, 350))   # 左手
        self._render_player(3, (1050, 350)) # 右手

        # 渲染当前出牌
        if self.game.last_play:
            self._render_cards(self.game.last_play, (600, 350))

        # 渲染选中的牌
        if self.selected_cards:
            self._render_cards(self.selected_cards, (600, 600), selected=True)

        pygame.display.flip()

    def _render_player(self, player_id: int, pos: tuple):
        """渲染玩家"""
        player = self.game.players[player_id]
        x, y = pos

        if player_id == 0:  # 己方
            card_width = 80
            for i, card in enumerate(player.hand):
                cx = x - (len(player.hand) * card_width) // 2 + i * card_width
                self._render_card(card, (cx, y), face_up=True)

    def _render_cards(self, cards: list[Card], pos: tuple, selected: bool = False):
        """渲染一组牌"""
        x, y = pos
        for i, card in enumerate(cards):
            self._render_card(card, (x + i * 30, y), selected=selected)

    def _render_card(self, card: Card, pos: tuple, face_up: bool = True, selected: bool = False):
        """渲染单张牌"""
        x, y = pos

        # 牌框
        color = (255, 255, 255) if face_up else (100, 100, 200)
        rect = pygame.Rect(x, y, 80, 120)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

        if selected:
            pygame.draw.rect(self.screen, (255, 255, 0), rect, 4)

        if face_up:
            # 绘制牌面
            font = pygame.font.Font(None, 36)
            text = font.render(str(card), True, (0, 0, 0) if card.suit in (Suit.SPADE, Suit.CLUB) else (255, 0, 0))
            self.screen.blit(text, (x + 20, y + 40))

if __name__ == '__main__':
    ui = GuandanUI()
    ui.run()
```

- [ ] **Step 3: Write guandan_ui/renderer.py**

```python
# PyGame渲染器（可选扩展）
# 当前实现放在main.py中，后续可拆分
```

- [ ] **Step 4: Commit**

```bash
git add guandan_ui/
git commit -m "feat: add pygame UI"
```

---

## Chunk 4: RL训练 (trainer)

### Task 9: 训练代码

**Files:**
- Create: `trainer/__init__.py`
- Create: `trainer/config.py`
- Create: `trainer/train.py`

- [ ] **Step 1: Write trainer/__init__.py**

```python
from trainer.train import train
from trainer.config import TrainConfig

__all__ = ['train', 'TrainConfig']
```

- [ ] **Step 2: Write trainer/config.py**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainConfig:
    algorithm: str = "PPO"
    total_timesteps: int = 1_000_000
    env_make_fn = None  # 环境创建函数
    model_kwargs: Optional[dict] = None
    save_freq: int = 10000
    eval_freq: int = 50000
    save_path: str = "./models"
    seed: int = 42

    def __post_init__(self):
        if self.model_kwargs is None:
            self.model_kwargs = {
                'policy': 'MlpPolicy',
                'learning_rate': 3e-4,
                'n_steps': 2048,
                'batch_size': 64,
                'n_epochs': 10,
                'gamma': 0.99,
            }
```

- [ ] **Step 3: Write trainer/train.py**

```python
import os
from stable_baselines3 import PPO, A2C
from guandan_gym.env import GuandanEnv

def train(config):
    """训练主函数"""
    # 创建环境
    env = GuandanEnv()

    # 创建模型
    if config.algorithm == "PPO":
        model = PPO(config.policy, env, **config.model_kwargs)
    elif config.algorithm == "A2C":
        model = A2C(config.policy, env, **config.model_kwargs)
    else:
        raise ValueError(f"Unknown algorithm: {config.algorithm}")

    # 训练
    model.learn(total_timesteps=config.total_timesteps)

    # 保存
    os.makedirs(config.save_path, exist_ok=True)
    model.save(os.path.join(config.save_path, f"{config.algorithm}_guandan"))

    return model

if __name__ == '__main__':
    from trainer.config import TrainConfig
    config = TrainConfig(
        algorithm="PPO",
        total_timesteps=100000,
    )
    train(config)
```

- [ ] **Step 4: Commit**

```bash
git add trainer/
git commit -m "feat: add RL training code"
```

---

## Chunk 5: 项目配置

### Task 10: 项目配置与README

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `requirements.txt`

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "guandan"
version = "0.1.0"
description = "掼蛋游戏RL训练平台"
requires-python = ">=3.10"
dependencies = [
    "gymnasium>=0.29.0",
    "stable-baselines3>=2.0.0",
    "pygame>=2.5.0",
    "numpy>=1.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 2: Write requirements.txt**

```
gymnasium>=0.29.0
stable-baselines3>=2.0.0
pygame>=2.5.0
numpy>=1.24.0
pytest>=7.0.0
```

- [ ] **Step 3: Write README.md**

```markdown
# 掼蛋RL训练平台

掼蛋是一种四人扑克游戏，需要队友配合。本项目实现完整的掼蛋游戏引擎和RL训练环境。

## 特性

- 完整掼蛋规则引擎
- Gymnasium RL环境
- PyGame人机对战UI
- 支持PPO/A2C等算法训练

## 安装

```bash
pip install -e .
```

## 训练

```bash
python -m trainer.train
```

## 游戏

```bash
python -m guandan_ui.main
```

## 测试

```bash
pytest tests/
```
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml requirements.txt README.md
git commit -m "chore: add project configuration"
```

---

## 实施顺序

1. **Phase 1: 核心引擎** (Task 1-6)
   - 先完成牌型定义和判断
   - 再完成玩家、游戏逻辑
   - 验收：游戏可以发牌、出牌、判断胜负

2. **Phase 2: RL环境** (Task 7)
   - 封装Gymnasium环境
   - 验收：`make_vec_env` 可用于训练

3. **Phase 3: UI** (Task 8)
   - 简化版UI
   - 验收：可以人机对战

4. **Phase 4: 训练** (Task 9)
   - 训练脚本
   - 验收：模型可以收敛

5. **Phase 5: 配置** (Task 10)
   - 项目配置
   - 验收：项目可安装运行
