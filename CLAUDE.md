# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Guandan (掼蛋) is a popular Chinese card game - a four-player partnership game similar to Dou Di Zhu. This project implements a complete Guandan game platform with RL training capabilities.

## Architecture

```
guandan/
├── guandan_core/      # Core game engine (no external dependencies)
├── guandan_gym/       # Gymnasium RL environment
├── guandan_ui/        # PyGame UI for human-AI gameplay
└── trainer/           # RL training scripts
```

## Commands

### Run the game UI
```bash
python -m guandan_ui.main
```

### Run RL training
```bash
python -m trainer.train
```

### Run tests
```bash
pytest
```

## Dependencies

- guandan_core: Pure Python, no external dependencies
- guandan_gym: Depends on core + gymnasium
- guandan_ui: Depends on core + pygame
- trainer: Depends on gym + stable-baselines3

## Game Controls (PyGame UI)

- Left click: Select cards / Play cards
- Right click: Pass (不出)
- Space: Play selected cards
- H: Show hint
- R: Restart game
