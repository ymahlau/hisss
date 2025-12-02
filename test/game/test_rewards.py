import unittest

import numpy as np

from hisss.game.battlesnake import DOWN, LEFT, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig
from hisss.game.rewards import KillBattleSnakeRewardConfig
from test.bootcamp.test_envs_9x9 import survive_on_9x9_constrictor_4_player


class TestRewards(unittest.TestCase):
    def test_win_no_legal(self):
        init_pos = {0: [[0, 1], [1, 1], [0, 2]], 1: [[2, 2], [2, 1], [2, 0]]}
        cfg = BattleSnakeConfig(w=3, h=3, num_players=2, constrictor=True, init_snake_pos=init_pos,
                                init_snake_len=[3, 3], init_snake_health=[5, 5], all_actions_legal=False)
        game = BattleSnakeGame(cfg)
        game.render()
        reward, done, info = game.step((DOWN, LEFT))
        game.render()
        self.assertTrue(done)
        self.assertEqual(1, reward[0])
        self.assertEqual(-1, reward[1])
        self.assertTrue(game.is_terminal())

