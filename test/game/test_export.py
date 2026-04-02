import json
import unittest

from hisss.game.battlesnake import UP, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig
from hisss.game.export import to_battlesnake_json


def _duel_game():
    gc = BattleSnakeConfig(
        w=11,
        h=11,
        num_players=2,
        min_food=1,
        food_spawn_chance=15,
        init_snake_pos={0: [[0, 0]], 1: [[10, 10]]},
        init_food_pos=[[5, 5]],
        init_snake_len=[3, 3],
        all_actions_legal=True,
    )
    return BattleSnakeGame(gc)


class TestToBattlesnakeJson(unittest.TestCase):
    def test_top_level_keys(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIn("game", data)
        self.assertIn("turn", data)
        self.assertIn("board", data)
        self.assertIn("you", data)
        game.close()

    def test_board_dimensions(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual(11, data["board"]["height"])
        self.assertEqual(11, data["board"]["width"])
        game.close()

    def test_food_present(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIn({"x": 5, "y": 5}, data["board"]["food"])
        game.close()

    def test_turn_counter(self):
        game = _duel_game()
        game.step((UP, UP))
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual(1, data["turn"])
        game.close()

    def test_you_matches_player(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 1))
        self.assertEqual("snake-1", data["you"]["id"])
        game.close()

    def test_snake_count_two_players(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual(2, len(data["board"]["snakes"]))
        game.close()

    def test_snake_count_alive_only(self):
        gc = BattleSnakeConfig(
            w=11,
            h=11,
            num_players=2,
            min_food=0,
            food_spawn_chance=0,
            init_snake_pos={0: [[0, 0]], 1: [[10, 5]]},
            init_food_pos=[],
            init_snake_len=[3, 3],
            init_snake_health=[1, 100],
            all_actions_legal=True,
        )
        game = BattleSnakeGame(gc)
        game.step((UP, UP))  # player 0 starves (health 1 → 0), player 1 survives
        data = json.loads(to_battlesnake_json(game, 1))
        self.assertEqual(1, len(data["board"]["snakes"]))
        self.assertEqual("snake-1", data["board"]["snakes"][0]["id"])
        game.close()

    def test_ruleset_name_standard(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual("standard", data["game"]["ruleset"]["name"])
        self.assertEqual("standard", data["game"]["map"])
        game.close()

    def test_ruleset_settings(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        settings = data["game"]["ruleset"]["settings"]
        self.assertEqual(15, settings["foodSpawnChance"])
        self.assertEqual(1, settings["minimumFood"])
        self.assertEqual(14, settings["hazardDamagePerTurn"])
        game.close()

    def test_ruleset_name_royale(self):
        gc = BattleSnakeConfig(
            w=11,
            h=11,
            num_players=2,
            royale=True,
            shrink_n_turns=25,
            init_snake_pos={0: [[0, 0]], 1: [[10, 10]]},
            init_food_pos=[[5, 5]],
            init_snake_len=[3, 3],
        )
        game = BattleSnakeGame(gc)
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual("royale", data["game"]["ruleset"]["name"])
        self.assertEqual("royale", data["game"]["map"])
        game.close()

    def test_hazards_royale(self):
        gc = BattleSnakeConfig(
            w=11,
            h=11,
            num_players=2,
            royale=True,
            shrink_n_turns=1,
            init_snake_pos={0: [[5, 5]], 1: [[6, 5]]},
            init_food_pos=[[0, 0]],
            init_snake_len=[3, 3],
            all_actions_legal=True,
        )
        game = BattleSnakeGame(gc)
        game.step((UP, UP))  # trigger first hazard ring
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertGreater(len(data["board"]["hazards"]), 0)
        game.close()

    def test_hazards_empty_standard(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual([], data["board"]["hazards"])
        game.close()

    def test_dead_player_raises(self):
        gc = BattleSnakeConfig(
            w=11,
            h=11,
            num_players=2,
            min_food=0,
            food_spawn_chance=0,
            init_snake_pos={0: [[0, 0]], 1: [[10, 10]]},
            init_food_pos=[],
            init_snake_len=[3, 3],
            init_snake_health=[1, 100],
            all_actions_legal=True,
        )
        game = BattleSnakeGame(gc)
        game.step((UP, UP))
        with self.assertRaises(ValueError):
            to_battlesnake_json(game, 0)
        game.close()

    def test_game_id_is_string(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIsInstance(data["game"]["id"], str)
        self.assertTrue(len(data["game"]["id"]) > 0)
        game.close()

    def test_snake_body_head_first(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        snake = next(s for s in data["board"]["snakes"] if s["id"] == "snake-0")
        self.assertEqual(snake["head"], snake["body"][0])
        game.close()
