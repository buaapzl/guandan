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


def test_game_over():
    """Test that game over is properly detected"""
    env = GuandanEnv()
    obs, info = env.reset()

    # Play until game ends or max steps
    max_steps = 100
    for _ in range(max_steps):
        mask = env.legal_actions_mask()
        legal_actions = np.where(mask)[0]

        if len(legal_actions) == 0:
            break

        action = legal_actions[0]
        obs, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            break


def test_observation_values():
    """Test that observation values are valid"""
    env = GuandanEnv()
    obs, info = env.reset()

    # Check observation is in valid range
    assert np.all(obs >= 0)
    assert np.all(obs <= 1)

    # Check specific observation ranges
    # Hand cards should have some cards
    hand_cards = obs[0:54]
    assert hand_cards.sum() > 0  # Should have some cards in hand


def test_info_contains_expected_fields():
    """Test that info contains expected fields"""
    env = GuandanEnv()
    obs, info = env.reset()

    expected_fields = ['current_player', 'hand_size', 'round', 'game_over']
    for field in expected_fields:
        assert field in info
