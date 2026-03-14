"""
队伍类
"""
from typing import Optional

from guandan_core.player import Player


class Team:
    """队伍类"""

    def __init__(self, team_id: int):
        self.team_id = team_id
        self.players: list[Player] = []
        self.level: int = 2  # 当前等级
        self.wins: int = 0   # 获胜次数

    def add_player(self, player: Player):
        """添加玩家到队伍"""
        self.players.append(player)

    def is_complete(self) -> bool:
        """是否满员（2人）"""
        return len(self.players) == 2

    def get_teammate(self, player: Player) -> Optional[Player]:
        """获取队友"""
        if not self.is_complete():
            return None

        for p in self.players:
            if p.player_id != player.player_id:
                return p
        return None

    def has_first_place(self) -> bool:
        """是否有头游（已实现，需要游戏状态判断）"""
        # 需要根据游戏状态判断，暂时返回False
        # 在实际游戏中会根据玩家出完牌的顺序来判断
        return False

    def __repr__(self) -> str:
        return f"Team({self.team_id}, 等级:{self.level}, 获胜:{self.wins}, 玩家:{len(self.players)}人)"
