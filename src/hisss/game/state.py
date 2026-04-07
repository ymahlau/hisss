from dataclasses import dataclass

CAUSE_INT_TO_STR: dict[int, str] = {
    1: "wall-collision",
    2: "out-of-health",
    3: "snake-self-collision",
    4: "snake-collision",
    5: "head-collision",
}
CAUSE_STR_TO_INT: dict[str, int] = {v: k for k, v in CAUSE_INT_TO_STR.items()}


@dataclass
class EliminationEvent:
    cause: str
    turn: int
    by: str | None = None


@dataclass
class BattleSnakeState:
    turn: int
    snakes_alive: list[bool]
    snake_pos: dict[int, list[tuple[int, int]]]  # includes dead snakes
    food_pos: list[list[int]]
    snake_health: list[int]  # includes dead snakes
    snake_len: list[int]  # includes dead snakes
    food_spawn_turns: list[int] | None = None
    elimination_events: dict[int, "EliminationEvent"] | None = None
