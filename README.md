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
