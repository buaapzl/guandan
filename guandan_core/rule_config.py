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
        return cls(
            use_joker=True,
            joker_can_be_bomb=False,
            use_sacrifice=True,
            can_resist_ace=True,
            return_card=True,
            first_level_up=2,
            protect_level=2,
            bomb_upgrade=True,
            bomb_upgrade_level=2,
        )

    @classmethod
    def simple(cls) -> 'RuleConfig':
        """简化规则（无贡牌）"""
        return cls(
            use_joker=True,
            joker_can_be_bomb=False,
            use_sacrifice=False,
            can_resist_ace=False,
            return_card=False,
            first_level_up=2,
            protect_level=2,
            bomb_upgrade=True,
            bomb_upgrade_level=2,
        )
