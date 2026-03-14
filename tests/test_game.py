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
    # 每人应该发27张牌
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
    actions = game.get_legal_actions(0)
    if actions:
        game.play_cards(0, actions[0])
        assert len(player.hand) < 27
