from dataclasses import dataclass, field
from typing import Optional

from hisss.game.encoding import (
    BattleSnakeEncodingConfig,
    BestBattleSnakeEncodingConfig,
    BestRestrictedEncodingConfig,
    SimpleBattleSnakeEncodingConfig,
)
from hisss.game.rewards import (
    BattleSnakeRewardConfig,
    KillBattleSnakeRewardConfig,
    StandardBattleSnakeRewardConfig,
)


@dataclass
class BattleSnakeConfig:
    """Configuration class for setting up a BattleSnake game environment.

    This dataclass holds all the parameters needed to initialize a game, including
    board dimensions, food spawn rates, snake initialization, game modes, and
    encoding/reward strategies for reinforcement learning environments.
    """

    #: Number of possible actions (default is 4: UP, DOWN, LEFT, RIGHT).
    num_actions: int = field(default=4)
    #: Total number of snakes in the game.
    num_players: int = field(default=2)

    # board
    #: Width of the game board.
    w: int = 5
    #: Height of the game board.
    h: int = 5

    # encoding
    #: Configuration for how the game state is encoded into neural network inputs.
    ec: BattleSnakeEncodingConfig = field(
        default_factory=SimpleBattleSnakeEncodingConfig
    )

    # snakes
    #: If True, ignores collision/bounds checking for legal action generation.
    all_actions_legal: bool = False
    #: Maximum health capacity for each snake.
    max_snake_health: Optional[list[int]] = None

    # food
    #: Minimum amount of food to keep on the board at all times.
    min_food: int = 1
    #: Probability (out of 100) of food spawning on a given turn.
    food_spawn_chance: int = 15

    # game state initialization
    #: Starting turn number for the game state.
    init_turns_played: int = 0
    #: Initial alive status for each snake. ``None`` implies all snakes are alive.
    init_snakes_alive: Optional[list[bool]] = None
    #: Fixed starting positions for snakes. ``None`` implies random spawning.
    init_snake_pos: Optional[dict[int, list[list[int]]]] = None
    #: Fixed starting positions for food. ``None`` spawns food randomly; ``[]`` spawns no food.
    init_food_pos: Optional[list[list[int]]] = None
    #: Starting health for each snake.
    init_snake_health: Optional[list[int]] = None
    #: Starting length for each snake.
    init_snake_len: Optional[list[int]] = None

    # rewards
    #: Configuration determining how rewards are assigned to snakes.
    reward_cfg: BattleSnakeRewardConfig = field(
        default_factory=StandardBattleSnakeRewardConfig
    )

    # special game modes
    #: If True, enables "Wrapped" mode where snakes can move through board edges.
    wrapped: bool = False
    #: If True, enables "Royale" mode with a shrinking hazard zone.
    royale: bool = False
    #: If True, enables "Constrictor" mode where snakes grow infinitely and leave a permanent trail.
    constrictor: bool = False
    #: Number of turns between hazard zone shrink events in Royale mode.
    shrink_n_turns: int = 25
    #: Amount of health lost per turn when a snake is inside a hazard zone.
    hazard_damage: int = 14
    #: Initial coordinates of hazard tiles.
    init_hazards: Optional[list[list[int]]] = None
    #: Radius of visibility for restricted modes. ``None`` implies full board visibility.
    view_radius: int | None = None


def post_init_battlesnake_cfg(cfg: BattleSnakeConfig):
    # default parameter initialization
    if cfg.init_hazards is None:
        cfg.init_hazards = []
    if cfg.init_snake_health is None:
        cfg.init_snake_health = [100 for _ in range(cfg.num_players)]
    if cfg.init_snake_len is None:
        cfg.init_snake_len = [3 for _ in range(cfg.num_players)]
    if cfg.max_snake_health is None:
        cfg.max_snake_health = [100 for _ in range(cfg.num_players)]
    if cfg.init_snakes_alive is None:
        cfg.init_snakes_alive = [True for _ in range(cfg.num_players)]
    if cfg.constrictor:
        cfg.init_snake_len = [cfg.w * cfg.h + 1 for _ in range(cfg.num_players)]
        cfg.init_snake_health = [cfg.w * cfg.h + 1 for _ in range(cfg.num_players)]
        cfg.max_snake_health = [cfg.w * cfg.h + 1 for _ in range(cfg.num_players)]
        cfg.init_hazards = []
        cfg.init_food_pos = []
        cfg.food_spawn_chance = 0
        cfg.min_food = 0


def validate_battlesnake_cfg(cfg: BattleSnakeConfig):
    # ran post init
    assert cfg.init_hazards is not None
    assert cfg.init_snake_health is not None
    assert cfg.init_snake_len is not None
    assert cfg.max_snake_health is not None
    # random spawning
    if cfg.init_food_pos is not None:
        assert len(cfg.init_food_pos) >= cfg.min_food
        if cfg.init_food_pos:
            assert cfg.init_snake_pos is not None, (
                "You cannot spawn snakes randomly and food fixed"
            )
    if cfg.init_snake_pos is not None:
        assert len(cfg.init_snake_pos) == cfg.num_players
        assert cfg.init_food_pos is not None, (
            "You cannot spawn snakes fixed and food randomly"
        )
    if cfg.w != cfg.h or cfg.w % 2 == 0 or cfg.h % 2 == 0:
        assert cfg.init_snake_pos is not None, (
            "Cannot spawn snakes randomly on weird board shapes"
        )
        assert cfg.init_food_pos is not None, (
            "Cannot spawn food randomly on weird board shapes"
        )
    # health, lengths, turns
    assert len(cfg.init_snake_health) == cfg.num_players
    for i in range(cfg.num_players):
        assert cfg.max_snake_health[i] >= cfg.init_snake_health[i]
    assert len(cfg.max_snake_health) == cfg.num_players
    assert len(cfg.init_snake_len) == cfg.num_players
    assert cfg.init_turns_played >= 0
    # game modes
    if cfg.w != cfg.h or cfg.w % 2 != 1:
        assert not cfg.ec.centered, (
            "Can only center observation in odd-sized square boards"
        )
    if cfg.wrapped:
        assert not cfg.ec.include_board, (
            "You do not want to include borders in wrapped mode"
        )
    if cfg.royale:
        assert cfg.w == cfg.h, "Royale Mode only works with square boards"
    if cfg.constrictor:
        assert len(cfg.init_hazards) == 0, "Constrictor does not work with hazards"
        assert not cfg.royale, "Constrictor does not work with royale"
    if cfg.view_radius is not None:
        assert cfg.ec.include_distance_map, (
            "Restricted mode needs distance map to calculate observation mask"
        )
        assert not cfg.ec.include_area_control, (
            "Restricted mode cannot use area control in observations"
        )
        assert not cfg.ec.include_food_distance, (
            "Restricted mode cannot use food distance in observations"
        )
        assert not cfg.ec.include_num_food_on_board, (
            "Restricted mode cannot use number of food on the board in obs"
        )
    if cfg.ec.include_view_mask:
        assert cfg.view_radius is not None, (
            "Can only include view mask in obs if view_radius is set in game config"
        )


def encoding_layer_indices(game_cfg: BattleSnakeConfig) -> dict[str, int]:
    """Generates a mapping of feature names to their depth index in the spatial encoding.

    This helps in constructing or interpreting the multi-channel grid encoding (tensor)
    fed into the neural network, mapping semantic names (like 'current_food' or
    '0_snake_head') to their specific z-axis index based on the chosen encoding config.

    Args:
        game_cfg (BattleSnakeConfig): The game configuration containing the encoding setup.

    Returns:
        dict[str, int]: A dictionary mapping the string name of the feature to its integer layer index.
    """

    ec = game_cfg.ec
    layer_counter = 0
    res_dict = {}
    # general layers for all snakes
    if ec.include_current_food:
        res_dict["current_food"] = layer_counter
        layer_counter += 1
    if ec.include_next_food:
        res_dict["next_food"] = layer_counter
        layer_counter += 1
    if ec.include_board:
        res_dict["board"] = layer_counter
        layer_counter += 1
    if ec.include_number_of_turns:
        res_dict["number_of_turns"] = layer_counter
        layer_counter += 1
    if ec.include_distance_map:
        res_dict["distance_map"] = layer_counter
        layer_counter += 1
    if ec.include_hazards:
        res_dict["hazards"] = layer_counter
        layer_counter += 1
    if ec.include_num_food_on_board:
        res_dict["num_food_on_board"] = layer_counter
        layer_counter += 1
    # snake specific layers
    num_snake_layers = 2 if ec.compress_enemies else game_cfg.num_players
    for p in range(num_snake_layers):
        if ec.include_snake_body:
            res_dict[f"{p}_snake_body"] = layer_counter
            layer_counter += 1
        if ec.include_snake_body_as_one_hot:
            res_dict[f"{p}_snake_body_as_one_hot"] = layer_counter
            layer_counter += 1
        if ec.include_snake_head:
            res_dict[f"{p}_snake_head"] = layer_counter
            layer_counter += 1
        if ec.include_snake_tail:
            res_dict[f"{p}_snake_tail"] = layer_counter
            layer_counter += 1
        if ec.include_snake_health:
            res_dict[f"{p}_snake_health"] = layer_counter
            layer_counter += 1
        if ec.include_snake_length:
            res_dict[f"{p}_snake_length"] = layer_counter
            layer_counter += 1
        if ec.include_area_control:
            res_dict[f"{p}_area_control"] = layer_counter
            layer_counter += 1
        if ec.include_food_distance:
            res_dict[f"{p}_food_distance"] = layer_counter
            layer_counter += 1
        if ec.include_tail_distance:
            res_dict[f"{p}_tail_distance"] = layer_counter
            layer_counter += 1
    if ec.include_view_mask:
        res_dict["view_mask"] = layer_counter
        layer_counter += 1
    return res_dict


def duel_config() -> BattleSnakeConfig:
    """Creates a preset configuration for a standard 2-player Duel game.

    Sets up an 11x11 board for 2 players using the best available encoding without
    enemy compression. Uses the standard reward configuration.

    Returns:
        BattleSnakeConfig: The configured duel environment settings.
    """
    ec = BestBattleSnakeEncodingConfig()
    ec.compress_enemies = False
    gc = BattleSnakeConfig(
        w=11,
        h=11,
        num_players=2,
        min_food=1,
        food_spawn_chance=15,
        ec=ec,
        init_snake_len=[3, 3],
        all_actions_legal=False,
        reward_cfg=StandardBattleSnakeRewardConfig(),
    )
    return gc


def standard_config() -> BattleSnakeConfig:
    """Creates a preset configuration for a standard 4-player game.

    Sets up an 11x11 board for 4 players using the best available encoding.
    Uses the kill-based reward configuration.

    Returns:
        BattleSnakeConfig: The configured standard environment settings.
    """
    ec = BestBattleSnakeEncodingConfig()
    gc = BattleSnakeConfig(
        w=11,
        h=11,
        num_players=4,
        min_food=1,
        food_spawn_chance=15,
        ec=ec,
        init_snake_len=[3, 3, 3, 3],
        all_actions_legal=False,
        reward_cfg=KillBattleSnakeRewardConfig(),
    )
    return gc


def restricted_standard_config() -> BattleSnakeConfig:
    """Creates a preset configuration for a 4-player Restricted game.

    Sets up a 15x15 board for 4 players where snake visibility is limited to a
    radius of 5 tiles (fog of war effect).

    Returns:
        BattleSnakeConfig: The configured restricted environment settings.
    """
    ec = BestRestrictedEncodingConfig()
    gc = BattleSnakeConfig(
        w=15,
        h=15,
        num_players=4,
        min_food=1,
        food_spawn_chance=15,
        ec=ec,
        init_snake_len=[3, 3, 3, 3],
        all_actions_legal=False,
        reward_cfg=KillBattleSnakeRewardConfig(),
        view_radius=5,
    )
    return gc


def restricted_duel_config() -> BattleSnakeConfig:
    """Creates a preset configuration for a 2-player Restricted Duel game.

    Sets up a 15x15 board for 2 players where snake visibility is limited to a
    radius of 5 tiles (fog of war effect), without compressing enemy encodings.

    Returns:
        BattleSnakeConfig: The configured restricted duel environment settings.
    """
    ec = BestRestrictedEncodingConfig()
    ec.compress_enemies = False
    gc = BattleSnakeConfig(
        w=15,
        h=15,
        num_players=2,
        min_food=1,
        food_spawn_chance=15,
        ec=ec,
        init_snake_len=[3, 3],
        all_actions_legal=False,
        reward_cfg=StandardBattleSnakeRewardConfig(),
        view_radius=5,
    )
    return gc
