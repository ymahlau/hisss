import json
import unittest

from hisss.game.battlesnake import UP, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig
from hisss.game.encoding import SimpleBattleSnakeEncodingConfig
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


def _restricted_game(view_radius=3, snake0_pos=None, snake1_pos=None, food_pos=None):
    ec = SimpleBattleSnakeEncodingConfig(include_distance_map=True)
    gc = BattleSnakeConfig(
        w=11,
        h=11,
        num_players=2,
        min_food=0,
        food_spawn_chance=0,
        init_snake_pos={0: snake0_pos or [[5, 5]], 1: snake1_pos or [[9, 9]]},
        init_food_pos=food_pos or [],
        init_snake_len=[3, 3],
        all_actions_legal=True,
        ec=ec,
        view_radius=view_radius,
    )
    return BattleSnakeGame(gc)


class TestRestrictedExport(unittest.TestCase):
    # Food visibility

    def test_food_outside_radius_hidden(self):
        # food at [0,0], player head at [5,5], radius=3 → distance=10 > 3
        game = _restricted_game(view_radius=3, food_pos=[[0, 0]])
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual([], data["board"]["food"])
        game.close()

    def test_food_within_radius_visible(self):
        # food at [5,6], distance=1 ≤ 3
        game = _restricted_game(view_radius=3, food_pos=[[5, 6]])
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIn({"x": 5, "y": 6}, data["board"]["food"])
        game.close()

    def test_food_exactly_at_radius_visible(self):
        # food at [5,8], distance=3 = radius=3
        game = _restricted_game(view_radius=3, food_pos=[[5, 8]])
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIn({"x": 5, "y": 8}, data["board"]["food"])
        game.close()

    def test_food_just_outside_radius_hidden(self):
        # food at [5,9], distance=4 > radius=3
        game = _restricted_game(view_radius=3, food_pos=[[5, 9]])
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual([], data["board"]["food"])
        game.close()

    # Own snake

    def test_own_snake_full_health(self):
        game = _restricted_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertGreater(data["you"]["health"], 0)
        game.close()

    def test_own_snake_no_tokens(self):
        game = _restricted_game()
        data = json.loads(to_battlesnake_json(game, 0))
        for seg in data["you"]["body"]:
            self.assertNotEqual({"x": -1, "y": -1}, seg)
        game.close()

    def test_own_snake_real_length(self):
        game = _restricted_game()
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertEqual(3, data["you"]["length"])
        game.close()

    # Fully hidden enemy

    def test_fully_hidden_enemy_absent(self):
        # player 0 at [5,5], player 1 at [9,9], distance=8 > radius=3
        game = _restricted_game(view_radius=3)
        data = json.loads(to_battlesnake_json(game, 0))
        ids = [s["id"] for s in data["board"]["snakes"]]
        self.assertNotIn("snake-1", ids)
        game.close()

    def test_fully_hidden_enemy_absent_from_you_perspective(self):
        # player 1's perspective: player 0 at [5,5] is distance 8 away from [9,9]
        game = _restricted_game(view_radius=3)
        data = json.loads(to_battlesnake_json(game, 1))
        ids = [s["id"] for s in data["board"]["snakes"]]
        self.assertNotIn("snake-0", ids)
        game.close()

    # Visible enemy

    def test_visible_enemy_health_zero(self):
        # player 0 at [5,5], player 1 at [6,5], distance=1 ≤ 3
        game = _restricted_game(view_radius=3, snake1_pos=[[6, 5]])
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertEqual(0, enemy["health"])
        game.close()

    def test_visible_enemy_in_board_snakes(self):
        game = _restricted_game(view_radius=3, snake1_pos=[[6, 5]])
        data = json.loads(to_battlesnake_json(game, 0))
        ids = [s["id"] for s in data["board"]["snakes"]]
        self.assertIn("snake-1", ids)
        game.close()

    # Token insertion: hidden head, visible body

    def test_hidden_head_visible_body_leading_token(self):
        # player 0 head at [5,5], radius=2
        # player 1 head at [8,5] (distance=3, hidden), body at [7,5],[6,5] (dist 2,1, visible)
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[8, 5], [7, 5], [6, 5]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertEqual({"x": -1, "y": -1}, enemy["body"][0])
        game.close()

    def test_hidden_head_sets_head_field_to_token(self):
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[8, 5], [7, 5], [6, 5]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertEqual({"x": -1, "y": -1}, enemy["head"])
        game.close()

    # Token insertion: visible head, hidden tail

    def test_visible_head_hidden_tail_trailing_token(self):
        # player 0 head at [5,5], radius=2
        # player 1 head at [5,6] (dist 1), body at [5,7] (dist 2), tail at [5,8] (dist 3, hidden)
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[5, 6], [5, 7], [5, 8]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertEqual({"x": -1, "y": -1}, enemy["body"][-1])
        game.close()

    def test_visible_head_no_leading_token(self):
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[5, 6], [5, 7], [5, 8]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertNotEqual({"x": -1, "y": -1}, enemy["body"][0])
        game.close()

    # Length equals body list length (lower bound)

    def test_length_equals_body_list_length(self):
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[8, 5], [7, 5], [6, 5]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertEqual(len(enemy["body"]), enemy["length"])
        game.close()

    def test_length_lower_bound_with_tokens(self):
        # body has leading token: [{-1,-1}, {7,5}, {6,5}] → length=3, real length=3
        # For a longer snake the token would compress multiple hidden segments
        game = _restricted_game(
            view_radius=2,
            snake1_pos=[[8, 5], [7, 5], [6, 5]],
        )
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        # Real body has 3 segments; exported body [{-1,-1}, {7,5}, {6,5}] has length 3
        self.assertEqual(3, enemy["length"])
        game.close()

    # Unrestricted mode unaffected

    def test_unrestricted_enemy_health_nonzero(self):
        game = _duel_game()
        data = json.loads(to_battlesnake_json(game, 0))
        enemy = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertGreater(enemy["health"], 0)
        game.close()

    def test_unrestricted_all_food_visible(self):
        gc = BattleSnakeConfig(
            w=11,
            h=11,
            num_players=2,
            min_food=1,
            food_spawn_chance=0,
            init_snake_pos={0: [[5, 5]], 1: [[9, 9]]},
            init_food_pos=[[0, 0]],
            init_snake_len=[3, 3],
            all_actions_legal=True,
        )
        game = BattleSnakeGame(gc)
        data = json.loads(to_battlesnake_json(game, 0))
        self.assertIn({"x": 0, "y": 0}, data["board"]["food"])
        game.close()
