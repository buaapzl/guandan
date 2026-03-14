# 掼蛋游戏RL训练平台设计

## 1. 项目概述

掼蛋是一种四人扑克游戏，需要队友配合。本项目旨在构建一个完整的掼蛋游戏平台，支持：
- 完整的掼蛋规则引擎
- 基于Gymnasium的RL训练环境
- PyGame人机对战UI
- 可训练、可扩展的AI玩家

## 2. 架构设计

### 2.1 分层架构

```
guandan/
├── guandan_core/      # 核心游戏引擎（无外部依赖）
│   ├── cards.py       # 扑克牌定义与工具
│   ├── player.py      # 玩家类
│   ├── team.py        # 队伍信息管理
│   ├── game.py        # 游戏主逻辑
│   ├── judge.py       # 牌型判断与比较
│   ├── recorder.py    # 记牌器
│   ├── calculator.py  # 算牌器
│   └── rule_config.py # 规则配置
│
├── guandan_gym/       # Gymnasium RL环境
│   ├── env.py         # Gymnasium环境实现
│   ├── obs_space.py   # 观察空间
│   └── action_space.py # 动作空间
│
├── guandan_ui/        # PyGame UI
│   ├── main.py        # 游戏主界面
│   ├── renderer.py    # 渲染器
│   └── controller.py  # 输入控制
│
└── trainer/           # RL训练
    ├── train.py       # 训练入口
    └── config.py      # 训练配置
```

### 2.2 依赖关系

- `guandan_core`: 纯Python，无外部依赖
- `guandan_gym`: 依赖 core + gymnasium
- `guandan_ui`: 依赖 core + pygame
- `trainer`: 依赖 gym + stable-baselines3

## 3. 核心游戏引擎 (guandan_core)

### 3.1 牌型定义

| 牌型 | 说明 |
|------|------|
| **单张** | 任意单张牌 |
| **对子** | 两张点数相同的牌 |
| **三张** | 三张点数相同的牌 |
| **三带二** | 三张相同点数 + 一对 |
| **顺子** | 5张连续点数（2不能参与顺子，A在K后循环） |
| **连对** | 3对连续对子 |
| **钢板** | 两个三张333444 |
| **炸弹** | 4张及以上相同点数 |
| **软炸弹** | 含有癞子的炸弹 |
| **天王炸弹** | 四张王（最大炸弹） |

### 3.1.1 逢人配（癞子）规则

- 大小王作为癞子，可配成除炸弹外的任意牌型
- 癞子**不能**配成炸弹
- 软炸弹需要按牌型大小比较

### 3.2 优先级规则

**基础规则：**
1. 首家出牌后，按逆时针轮流出牌
2. 必须大过上家牌型，或使用炸弹
3. 炸弹可以压任意牌型

**贡牌规则：**
1. 下游需向上游进贡（进贡最大的牌）
2. 头游抓A/K可抗贡
3. 还贡需小于进贡的牌
4. 首家出牌规则（进贡后由上游首家出牌）

**升级规则：**
1. 头游冲几：头游决定本局升级数
2. 二游保几：二游保证升级数不低于某值
3. 双下（对家双下）升级更多

**炸弹升级：**
1. 最后一手牌为炸弹，炸弹可升级
2. 炸弹升级后大于天王炸弹

### 3.3 记牌器

```python
class Recorder:
    # 跟踪已打出的所有牌
    # 提供剩余牌统计
    # 支持查询特定牌是否已打完
```

### 3.4 规则配置引擎

```python
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
```

### 3.5 算牌器

```python
class Calculator:
    # 根据已打出的牌和手牌
    # 计算对手可能持有的牌
    # 评估各牌型的危险程度
```

## 4. Gymnasium环境 (guandan_gym)

### 4.1 观察空间

使用Box空间，维度约为 280+ 维：

| 特征 | 描述 | 维度 |
|------|------|------|
| hand_cards | 手牌编码 | 54 |
| played_cards | 已打出的牌 | 54 |
| last_play | 上家出牌 | 54 |
| recorder_info | 记牌信息 | 54 |
| team_info | 等级/升级状态 | 4 |
| sacrifice_info | 贡牌信息 | 4 |
| last_two_plays | 最近两手牌 | 108 |
| game_state | 游戏状态 | 4 |
| position | 当前位置 | 4 |

### 4.2 动作空间

- 使用 **MultiDiscrete** 空间或分层动作空间
- 必须实现 `legal_actions_mask()` 方法，返回当前合法动作掩码
- 动作编码：先选牌型，再选具体牌

### 4.3 奖励设计

采用更密集的奖励信号：

| 奖励 | 值 | 描述 |
|------|-----|------|
| game_win | +1.0 | 己方获胜 |
| game_lose | -1.0 | 己方失败 |
| teammate_first | +0.3 | 队友头游 |
| teammate_second | +0.1 | 队友二游 |
| round_win | +0.2 | 一轮结束时获得出牌权 |
| sacrifice | -0.1 | 被贡走 |
| play_cards | -0.001 | 每出一手牌（轻微惩罚） |

### 4.4 环境接口

```python
class GuandanEnv(gym.Env):
    def reset(self, seed=None): ...
    def step(self, action): ...
    def render(self): ...
    def close(self): ...
    def legal_actions(self): ...    # 返回当前合法动作列表
    def legal_actions_mask(self): ...  # 返回合法动作掩码

### 4.4 环境接口

```python
class GuandanEnv(gym.Env):
    def reset(self, seed=None): ...
    def step(self, action): ...
    def render(self): ...
    def close(self): ...
    def legal_actions(self): ...  # 返回当前合法动作
```

## 5. PyGame UI (guandan_ui)

### 5.1 界面布局

```
┌─────────────────────────────────────────┐
│              队友（北家）               │
│  ┌─────┐                          ┌─────┐ │
│  │     │                          │     │ │
│  └─────┘                          └─────┘ │
│                                         │
│  对手（西家）     牌桌      对手（东家） │
│                                         │
│  ┌─────┐                          ┌─────┐ │
│  │     │                          │     │ │
│  └─────┘                          └─────┘ │
│                                         │
│              ┌─────────────┐            │
│              │   当前出牌   │            │
│              └─────────────┘            │
│                                         │
│            ┌───────────────┐             │
│            │   你的手牌    │             │
│            └───────────────┘             │
│              玩家（南家）                │
└─────────────────────────────────────────┘
```

### 5.2 交互功能

- 点击选牌
- 右键取消选择
- 出牌按钮
- 提示按钮（显示AI建议）
- 游戏信息显示
- **记牌器显示**：显示已打出和剩余牌
- **等级显示**：当前级数和升级状态
- **贡牌界面**：进贡/还贡交互
- **AI思考显示**：显示AI正在考虑的选项

## 6. RL训练 (trainer)

### 6.1 训练配置

```python
@dataclass
class TrainConfig:
    algorithm: str = "PPO"
    total_timesteps: int = 1_000_000
    env_make_kwargs: dict = None
    model_kwargs: dict = None
    save_freq: int = 10000
    eval_freq: int = 50000
```

### 6.2 支持的算法

- PPO (推荐)
- A2C
- DQN (离散动作)

### 6.3 训练流程

1. 初始化4个玩家（2个AI队友 + 2个AI对手）
2. 每轮收集经验
3. 更新策略网络
4. 定期评估 vs 随机/规则玩家
5. 保存最佳模型

## 7. 实施计划

### Phase 1: 核心引擎
- 牌型定义与比较
- 游戏流程控制
- 记牌器、算牌器

### Phase 2: RL环境
- Gymnasium接口实现
- 观察/动作空间定义
- 奖励函数

### Phase 3: UI
- PyGame基础界面
- 人机对战交互

### Phase 4: 训练
- 训练脚本
- 模型评估
- 人机对战模式

## 8. 扩展性

- 核心引擎独立，可直接用于其他项目
- 环境接口符合Gymnasium标准，易于接入新算法
- UI层可替换为Web/终端
- 可添加蒙特卡洛树搜索等高级策略
