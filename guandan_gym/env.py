"""
掼蛋Gymnasium环境
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List

from guandan_core.game import GuandanGame
from guandan_core.cards import Card
from guandan_core.player import Player


class GuandanEnv(gym.Env):
    """掼蛋Gymnasium环境"""

    metadata = {'render_modes': ['human']}

    def __init__(self, render_mode: Optional[str] = None):
        super().__init__()

        self.render_mode = render_mode
        self.game: Optional[GuandanGame] = None
        self._action_to_cards: Dict[int, List[Card]] = {}
        self._cards_to_action: Dict[tuple, int] = {}
        self._next_action_id: int = 1  # 0 is reserved for pass
        self._game_over: bool = False
        self._my_team_id: int = 0  # Team 0: players 0 and 2

        self._init_game()

        # 观察空间：54张牌的各种特征
        # 0-53: 手牌 (54维)
        # 54-107: 已打出的牌 (54维)
        # 108-161: 上家出牌 (54维)
        # 162-165: 游戏状态 (4维)
        # 166-169: 等级信息 (4维)
        # 170-279: 预留 (110维)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(280,), dtype=np.float32
        )

        # 动作空间：离散空间
        self.action_space = spaces.Discrete(2000)

    def _init_game(self):
        """初始化游戏"""
        self.game = GuandanGame()
        self.game.deal_cards()
        self._build_action_mapping()
        self._game_over = False

    def _build_action_mapping(self):
        """构建动作到卡牌的映射"""
        self._action_to_cards = {0: []}  # 0 is pass
        self._cards_to_action = {(): 0}
        self._next_action_id = 1

        # Get all playable cards for current player
        legal_actions = self.game.get_legal_actions(self.game.current_player)
        for cards in legal_actions:
            if self._next_action_id >= 2000:
                break
            key = tuple(c.to_index() for c in sorted(cards, key=lambda x: x.to_index()))
            if key not in self._cards_to_action:
                self._cards_to_action[key] = self._next_action_id
                self._action_to_cards[self._next_action_id] = cards
                self._next_action_id += 1

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, dict]:
        """重置环境"""
        super().reset(seed=seed)

        self._init_game()
        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """执行动作"""
        # Validate action
        if action < 0 or action >= self.action_space.n:
            raise ValueError(f"Invalid action: {action}")

        # Handle pass action
        if action == 0:
            # Player passes - move to next player
            self._next_player_step()
        else:
            # Play cards
            cards = self._action_to_cards.get(action, [])
            if not cards:
                # Invalid action, treat as pass
                self._next_player_step()
            else:
                self.game.play_cards(self.game.current_player, cards)

        # Check if game is over
        self._check_game_over()

        # Get observation, reward, and info
        obs = self._get_observation()
        reward = self._compute_reward()
        terminated = self._game_over
        truncated = False
        info = self._get_info()

        # Rebuild action mapping for new state
        if not self._game_over:
            self._build_action_mapping()

        return obs, reward, terminated, truncated, info

    def _next_player_step(self):
        """处理玩家过牌后的步骤"""
        # In the current game implementation, pass is handled by not playing cards
        # Move to next player
        self.game.current_player = (self.game.current_player + 1) % 4

    def _check_game_over(self):
        """检查游戏是否结束"""
        # Check if any player has empty hand (won)
        for i, player in enumerate(self.game.players):
            if player.is_empty:
                self._game_over = True
                return

    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        obs = np.zeros(280, dtype=np.float32)

        if self.game is None:
            return obs

        # Current player is always player 0 for this implementation
        current_player_id = 0
        my_player = self.game.players[current_player_id]
        partner_player = self.game.players[2]  # Player 2 is partner

        # 0-53: Hand cards (54 dims)
        for card in my_player.hand:
            idx = card.to_index()
            if 0 <= idx < 54:
                obs[idx] = 1.0

        # 54-107: Played cards / partner cards indicator (54 dims)
        # For simplicity, mark cards that have been played
        played_cards = set()
        # Check played cards from recorder or game state
        for player in self.game.players:
            if hasattr(player, 'hand'):
                # Cards not in hand are either played or in bottom
                pass

        # 108-161: Opponent's last play (54 dims)
        # Get the last play from opponent (player 1 or 3)
        if self.game.current_play:
            for player_id in [1, 3]:  # opponents
                if player_id < len(self.game.current_play):
                    last_play = self.game.current_play[player_id]
                    if last_play:
                        for card in last_play:
                            idx = card.to_index()
                            if 108 <= idx + 108 < 162:
                                obs[108 + idx] = 1.0

        # 162-165: Game state (4 dims)
        # 162: current player (normalized)
        obs[162] = self.game.current_player / 3.0
        # 163: round (normalized)
        obs[163] = min(self.game.round / 20.0, 1.0)
        # 164: is first player (1 if current player is first player)
        obs[164] = 1.0 if self.game.first_player == current_player_id else 0.0
        # 165: number of cards played this round
        played_count = sum(1 for p in self.game.current_play if p is not None)
        obs[165] = played_count / 4.0

        # 166-169: Level information (4 dims)
        # 166: my team level
        my_team = self.game.teams[self._my_team_id]
        obs[166] = my_team.level / 15.0
        # 167: opponent team level
        opp_team = self.game.teams[1 - self._my_team_id]
        obs[167] = opp_team.level / 15.0
        # 168: my team wins
        obs[168] = min(my_team.wins / 10.0, 1.0)
        # 169: opponent team wins
        obs[169] = min(opp_team.wins / 10.0, 1.0)

        # 170-279: Reserved (110 dims)
        # Currently all zeros

        return obs

    def _compute_reward(self) -> float:
        """计算奖励"""
        if not self._game_over:
            return 0.0

        # Check if my team won
        # Team 0: players 0 and 2
        my_player_won = self.game.players[0].is_empty or self.game.players[2].is_empty

        if my_player_won:
            return 1.0
        else:
            return -1.0

    def _get_info(self) -> dict:
        """获取额外信息"""
        if self.game is None:
            return {}

        current_player_id = 0  # Always player 0 for this implementation
        my_player = self.game.players[current_player_id]

        return {
            'current_player': current_player_id,
            'hand_size': len(my_player.hand),
            'round': self.game.round,
            'my_team_level': self.game.teams[self._my_team_id].level,
            'opp_team_level': self.game.teams[1 - self._my_team_id].level,
            'legal_actions_count': len(self._action_to_cards),
            'game_over': self._game_over,
        }

    def legal_actions_mask(self) -> np.ndarray:
        """获取合法动作掩码"""
        mask = np.zeros(self.action_space.n, dtype=np.float32)

        # Mark all valid actions
        for action_id in self._action_to_cards.keys():
            if action_id < self.action_space.n:
                mask[action_id] = 1.0

        return mask

    def render(self):
        """渲染环境"""
        if self.render_mode == 'human':
            print(f"Current player: {self.game.current_player}")
            print(f"Player 0 hand: {self.game.players[0].hand}")
            print(f"Round: {self.game.round}")
            if self.game.current_play:
                print(f"Current play: {self.game.current_play}")

    def close(self):
        """关闭环境"""
        self.game = None
