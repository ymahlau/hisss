import json
import uuid

import numpy as np

from hisss.game.battlesnake import BattleSnakeGame


_SNAKE_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 128, 0),
    (128, 0, 255),
]


def _ruleset_name(cfg) -> str:
    if cfg.wrapped:
        return "wrapped"
    if cfg.royale:
        return "royale"
    if cfg.constrictor:
        return "constrictor"
    return "standard"


def _map_name(cfg) -> str:
    if cfg.royale:
        return "royale"
    return "standard"


def to_battlesnake_json(
    game: BattleSnakeGame, player: int, include_eliminated: bool = False
) -> str:
    """Serialize a BattleSnakeGame state to a Battlesnake API-compatible JSON string.

    Args:
        game: The game instance to serialize.
        player: Zero-based index of the player whose perspective to use as ``"you"``.
        include_eliminated: When ``True``, dead snakes are included in
            ``board.snakes`` with an ``"elimination"`` key describing how they died.

    Returns:
        JSON string matching the Battlesnake API ``/move`` request body format.

    Raises:
        ValueError: If the game is closed or if ``player`` is not alive.
    """
    if game.is_closed:
        raise ValueError("Cannot serialize a closed game")
    if not game.is_player_alive(player):
        raise ValueError(f"Player {player} is not alive")

    cfg = game.cfg
    view_radius = cfg.view_radius

    if view_radius is not None:
        ph = game.player_pos(player)
        player_hx, player_hy = int(ph[0][0]), int(ph[0][1])

        def _visible(x: int, y: int) -> bool:
            return abs(x - player_hx) + abs(y - player_hy) <= view_radius

        def _build_restricted_body(body_coords):
            HIDDEN = {"x": -1, "y": -1}
            result = []
            in_hidden_run = False
            for x, y in body_coords:
                if _visible(int(x), int(y)):
                    in_hidden_run = False
                    result.append({"x": int(x), "y": int(y)})
                else:
                    if not in_hidden_run:
                        result.append(HIDDEN)
                        in_hidden_run = True
            if not any(seg != HIDDEN for seg in result):
                return []
            return result

    game_section = {
        "id": str(uuid.uuid4()),
        "ruleset": {
            "name": _ruleset_name(cfg),
            "version": "v1",
            "settings": {
                "foodSpawnChance": cfg.food_spawn_chance,
                "minimumFood": cfg.min_food,
                "hazardDamagePerTurn": cfg.hazard_damage,
                "viewRadius": view_radius,
                "royale": {"shrinkEveryNTurns": cfg.shrink_n_turns},
                "squad": {
                    "allowBodyCollisions": False,
                    "sharedElimination": False,
                    "sharedHealth": False,
                    "sharedLength": False,
                },
            },
        },
        "map": _map_name(cfg),
        "source": "hisss",
        "timeout": 500,
    }

    food_arr = game.food_pos()  # shape (n, 2), rows are [x, y]
    if view_radius is not None:
        spawn_turns = game.food_spawn_turns()
        food_list = [
            {"x": int(row[0]), "y": int(row[1]), "spawn_turn": int(spawn_turns[i])}
            for i, row in enumerate(food_arr)
            if _visible(int(row[0]), int(row[1])) or spawn_turns[i] == game.turns_played
        ]
    else:
        spawn_turns = game.food_spawn_turns()
        food_list = [
            {"x": int(row[0]), "y": int(row[1]), "spawn_turn": int(spawn_turns[i])}
            for i, row in enumerate(food_arr)
        ]

    hazard_arr = game.get_hazards()
    hazard_coords = np.argwhere(hazard_arr)
    hazards_list = [{"x": int(pos[0]), "y": int(pos[1])} for pos in hazard_coords]

    healths = game.player_healths()
    lengths = game.player_lengths()
    _state = game.get_state() if include_eliminated else None

    def _make_snake(p: int) -> dict | None:
        is_alive = game.is_player_alive(p)
        if not is_alive:
            if not include_eliminated:
                return None
            body_coords = game.player_pos(p)
            body_list = [{"x": int(x), "y": int(y)} for x, y in body_coords]
            head = body_list[0] if body_list else {"x": 0, "y": 0}
            snake_dict: dict = {
                "id": f"snake-{p}",
                "name": f"Snake {p}",
                "health": 0,
                "body": body_list,
                "latency": "0",
                "head": head,
                "length": int(lengths[p]),
                "shout": "",
                "squad": None,
                "customizations": {
                    "color": list(_SNAKE_COLORS[p % len(_SNAKE_COLORS)]),
                    "head": "default",
                    "tail": "default",
                },
            }
            if (
                _state is not None
                and _state.elimination_events
                and p in _state.elimination_events
            ):
                ev = _state.elimination_events[p]
                snake_dict["elimination"] = {
                    "cause": ev.cause,
                    "turn": ev.turn,
                    "by": ev.by,
                }
            return snake_dict
        body_coords = game.player_pos(p)
        if view_radius is None or p == player:
            body_list = [{"x": int(x), "y": int(y)} for x, y in body_coords]
            health = int(healths[p])
            length = int(lengths[p])
        else:
            body_list = _build_restricted_body(body_coords)
            if not body_list:
                body_list = [{"x": -1, "y": -1}]
            health = 0
            length = len(body_list)
        head = body_list[0] if body_list else {"x": 0, "y": 0}
        return {
            "id": f"snake-{p}",
            "name": f"Snake {p}",
            "health": health,
            "body": body_list,
            "latency": "0",
            "head": head,
            "length": length,
            "shout": "",
            "squad": None,
            "customizations": {
                "color": list(_SNAKE_COLORS[p % len(_SNAKE_COLORS)]),
                "head": "default",
                "tail": "default",
            },
        }

    snakes_list = [
        s for p in range(game.num_players) for s in [_make_snake(p)] if s is not None
    ]

    board_section = {
        "height": int(cfg.h),
        "width": int(cfg.w),
        "food": food_list,
        "hazards": hazards_list,
        "snakes": snakes_list,
    }

    return json.dumps(
        {
            "game": game_section,
            "turn": game.turns_played,
            "board": board_section,
            "you": _make_snake(player),
        }
    )
