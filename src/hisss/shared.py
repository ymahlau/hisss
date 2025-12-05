import copy
import random

import numpy as np

from hisss.game.battlesnake import BattleSnakeGame
from hisss.game.config import BattleSnakeConfig


def action_kills_player(
        game: BattleSnakeGame,
        player: int,
        ja: tuple[int, ...],
) -> bool:
    cpy = game.get_copy()
    cpy.step(ja)
    return player not in cpy.players_at_turn()


def step_with_draw_prevention(
        game: BattleSnakeGame,
        joint_actions: tuple[int, ...],
) -> np.ndarray:
    # computes a step, which prevents a draw between two players (if possible). Returns reward of the step
    # Also does not change the win chances for either player in repeated games (equal yield probability)
    if game.num_players_at_turn() != 2:
        # we can only correct deaths of two players
        rewards, _, _ = game.step(joint_actions)
        return rewards
    cpy = game.get_copy()
    cpy.step(joint_actions)
    if not cpy.is_terminal():
        # Either none or only one player died, which does not result in draw
        rewards, _, _ = game.step(joint_actions)
        return rewards
    # choose one of the players to yield for the other player
    yield_player_idx = np.random.randint(0, 2)
    yield_player = game.players_at_turn()[yield_player_idx]
    original_action = joint_actions[yield_player_idx]
    # check which other action do not kill yielding player
    possible_other_actions = []
    for action in game.available_actions(yield_player):
        if action == original_action:
            continue
        ja_cpy = list(copy.copy(joint_actions))
        ja_cpy[yield_player_idx] = action
        if not action_kills_player(game, yield_player, tuple(ja_cpy)):
            possible_other_actions.append(action)
    # if no other action is possible, then take original action
    if not possible_other_actions:
        rewards, _, _ = game.step(joint_actions)
        return rewards
    # choose random other action
    new_action = random.choice(possible_other_actions)
    new_ja = list(copy.copy(joint_actions))
    new_ja[yield_player_idx] = new_action
    rewards, _, _ = game.step(tuple(new_ja))
    return rewards
