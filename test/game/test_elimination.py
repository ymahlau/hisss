import json
import unittest

from hisss.game.battlesnake import DOWN, LEFT, UP, BattleSnakeGame
from hisss.game.config import BattleSnakeConfig
from hisss.game.export import to_battlesnake_json


def _make_game(
    snake_pos,
    food_pos=None,
    health=None,
    snake_len=None,
    w=11,
    h=11,
    wrapped=False,
):
    num_players = len(snake_pos)
    gc = BattleSnakeConfig(
        w=w,
        h=h,
        num_players=num_players,
        min_food=0,
        food_spawn_chance=0,
        init_snake_pos=snake_pos,
        init_food_pos=food_pos or [],
        init_snake_len=snake_len or [3] * num_players,
        init_snake_health=health,
        all_actions_legal=True,
        wrapped=wrapped,
    )
    return BattleSnakeGame(gc)


class TestEliminationCauses(unittest.TestCase):
    def test_starvation_cause(self):
        game = _make_game({0: [[5, 5]], 1: [[9, 9]]}, health=[1, 100])
        game.step((UP, UP))
        state = game.get_state()
        self.assertIsNotNone(state.elimination_events)
        self.assertIn(0, state.elimination_events)
        ev = state.elimination_events[0]
        self.assertEqual("out-of-health", ev.cause)
        self.assertEqual(0, ev.turn)
        self.assertIsNone(ev.by)
        game.close()

    def test_wall_collision_cause(self):
        # Snake at x=0, move LEFT goes out of bounds
        game = _make_game({0: [[0, 5]], 1: [[9, 9]]})
        game.step((LEFT, UP))
        state = game.get_state()
        self.assertIsNotNone(state.elimination_events)
        self.assertIn(0, state.elimination_events)
        ev = state.elimination_events[0]
        self.assertEqual("wall-collision", ev.cause)
        self.assertEqual(0, ev.turn)
        self.assertIsNone(ev.by)
        game.close()

    def test_body_collision_cause_and_killer(self):
        # Snake 0 occupies (5,5),(5,4),(5,3). Snake 1's head moves into (5,4) which is snake 0's body.
        game = _make_game(
            {0: [[5, 5], [5, 4], [5, 3]], 1: [[6, 4], [7, 4], [8, 4]]},
            snake_len=[3, 3],
        )
        # snake 1 moves LEFT into snake 0's body at (5,4)
        game.step((UP, LEFT))
        state = game.get_state()
        self.assertIsNotNone(state.elimination_events)
        self.assertIn(1, state.elimination_events)
        ev = state.elimination_events[1]
        self.assertEqual("snake-collision", ev.cause)
        self.assertEqual("snake-0", ev.by)
        game.close()

    def test_head_to_head_larger_wins(self):
        # Snake 0 (len=4) and snake 1 (len=3) meet heads at (5,5)
        # Snake 0 at (5,4) moves UP to (5,5); snake 1 at (5,6) moves DOWN to (5,5)
        game = _make_game(
            {0: [[5, 4], [5, 3], [5, 2], [5, 1]], 1: [[5, 6], [5, 7], [5, 8]]},
            snake_len=[4, 3],
        )
        game.step((UP, DOWN))
        state = game.get_state()
        self.assertIsNotNone(state.elimination_events)
        # Only snake 1 (smaller) should be eliminated
        self.assertIn(1, state.elimination_events)
        self.assertNotIn(0, state.elimination_events)
        ev = state.elimination_events[1]
        self.assertEqual("head-collision", ev.cause)
        self.assertEqual("snake-0", ev.by)
        game.close()

    def test_head_to_head_equal_size_both_die(self):
        # Both snakes length 3 meet heads — both die with head-collision
        game = _make_game(
            {0: [[5, 4], [5, 3], [5, 2]], 1: [[5, 6], [5, 7], [5, 8]]},
            snake_len=[3, 3],
        )
        game.step((UP, DOWN))
        state = game.get_state()
        self.assertIsNotNone(state.elimination_events)
        self.assertIn(0, state.elimination_events)
        self.assertIn(1, state.elimination_events)
        ev0 = state.elimination_events[0]
        ev1 = state.elimination_events[1]
        self.assertEqual("head-collision", ev0.cause)
        self.assertEqual("snake-1", ev0.by)
        self.assertEqual("head-collision", ev1.cause)
        self.assertEqual("snake-0", ev1.by)
        game.close()

    def test_alive_snake_not_in_elimination_events(self):
        game = _make_game({0: [[5, 5]], 1: [[9, 9]]}, health=[1, 100])
        game.step((UP, UP))
        state = game.get_state()
        # Snake 1 is alive — must not appear in elimination_events
        if state.elimination_events:
            self.assertNotIn(1, state.elimination_events)
        game.close()

    def test_elimination_turn_recorded(self):
        # Snake 0 at (2,5) moves LEFT twice to reach (0,5), then LEFT again to die on turn 2
        # Snake 1 at (5,5) moves UP to stay safely in bounds throughout
        game = _make_game({0: [[2, 5]], 1: [[5, 5]]})
        game.step((LEFT, UP))  # snake 0 → (1,5)
        game.step((LEFT, UP))  # snake 0 → (0,5)
        game.step((LEFT, UP))  # snake 0 → (-1,5) dies on turn 2
        state = game.get_state()
        self.assertIn(0, state.elimination_events)
        self.assertEqual(2, state.elimination_events[0].turn)
        game.close()


class TestEliminationStateRoundTrip(unittest.TestCase):
    def test_get_set_state_preserves_elimination(self):
        game = _make_game({0: [[0, 5]], 1: [[9, 9]]})
        game.step((LEFT, UP))  # snake 0 dies by wall on turn 0
        state = game.get_state()
        self.assertIn(0, state.elimination_events)

        # Restore to a fresh game
        game2 = _make_game({0: [[0, 5]], 1: [[9, 9]]})
        game2.set_state(state)
        state2 = game2.get_state()

        self.assertIsNotNone(state2.elimination_events)
        self.assertIn(0, state2.elimination_events)
        ev = state2.elimination_events[0]
        self.assertEqual("wall-collision", ev.cause)
        self.assertEqual(0, ev.turn)
        self.assertIsNone(ev.by)
        game.close()
        game2.close()

    def test_get_set_state_preserves_killer(self):
        game = _make_game(
            {0: [[5, 5], [5, 4], [5, 3]], 1: [[6, 4], [7, 4], [8, 4]]},
            snake_len=[3, 3],
        )
        game.step((UP, LEFT))
        state = game.get_state()
        self.assertIn(1, state.elimination_events)

        game2 = _make_game(
            {0: [[5, 5], [5, 4], [5, 3]], 1: [[6, 4], [7, 4], [8, 4]]},
            snake_len=[3, 3],
        )
        game2.set_state(state)
        state2 = game2.get_state()
        ev = state2.elimination_events[1]
        self.assertEqual("snake-collision", ev.cause)
        self.assertEqual("snake-0", ev.by)
        game.close()
        game2.close()


class TestEliminationReset(unittest.TestCase):
    def test_reset_clears_elimination_events(self):
        game = _make_game({0: [[0, 5]], 1: [[9, 9]]})
        game.step((LEFT, UP))
        state = game.get_state()
        self.assertIn(0, state.elimination_events)

        game.reset()
        state_after = game.get_state()
        # After reset no elimination events should exist
        self.assertTrue(
            state_after.elimination_events is None
            or len(state_after.elimination_events) == 0
        )
        game.close()


class TestEliminationJsonExport(unittest.TestCase):
    def _killed_game(self):
        game = _make_game({0: [[0, 5]], 1: [[9, 9]]})
        game.step((LEFT, UP))  # snake 0 dies by wall
        return game

    def test_export_without_flag_excludes_dead(self):
        game = self._killed_game()
        data = json.loads(to_battlesnake_json(game, 1))
        ids = [s["id"] for s in data["board"]["snakes"]]
        self.assertNotIn("snake-0", ids)
        game.close()

    def test_export_with_flag_includes_dead(self):
        game = self._killed_game()
        data = json.loads(to_battlesnake_json(game, 1, include_eliminated=True))
        ids = [s["id"] for s in data["board"]["snakes"]]
        self.assertIn("snake-0", ids)
        game.close()

    def test_export_elimination_event_fields(self):
        game = self._killed_game()
        data = json.loads(to_battlesnake_json(game, 1, include_eliminated=True))
        dead_snake = next(s for s in data["board"]["snakes"] if s["id"] == "snake-0")
        self.assertIn("elimination", dead_snake)
        elim = dead_snake["elimination"]
        self.assertIn("cause", elim)
        self.assertIn("turn", elim)
        self.assertIn("by", elim)
        self.assertEqual("wall-collision", elim["cause"])
        self.assertEqual(0, elim["turn"])
        self.assertIsNone(elim["by"])
        game.close()

    def test_export_alive_snake_has_no_elimination_key(self):
        game = self._killed_game()
        data = json.loads(to_battlesnake_json(game, 1, include_eliminated=True))
        alive_snake = next(s for s in data["board"]["snakes"] if s["id"] == "snake-1")
        self.assertNotIn("elimination", alive_snake)
        game.close()

    def test_export_default_no_dead_snakes(self):
        # Regression: default behavior still excludes dead snakes
        game = self._killed_game()
        data = json.loads(to_battlesnake_json(game, 1))
        self.assertEqual(1, len(data["board"]["snakes"]))
        game.close()
