from dataclasses import dataclass, field


@dataclass(kw_only=True)
class BattleSnakeEncodingConfig:
    """
    Configuration for encoding a BattleSnake game state into a NumPy tensor.

    This dataclass defines which specific spatial layers and global features
    should be included when translating the JSON-like game state into a numerical
    tensor representation, typically used as an observation space for reinforcement
    learning agents or neural networks.
    """

    #: bool: Includes a spatial layer representing the current locations of food on the board.
    include_current_food: bool

    #: bool: Includes a layer for predicted or upcoming food spawns, if supported by the environment.
    include_next_food: bool

    #: bool: Includes a base layer representing the playable board area (useful for identifying boundaries).
    include_board: bool

    #: bool: Includes the current turn number of the game as a feature.
    include_number_of_turns: bool

    #: bool: If True, all enemy snakes share the same encoding layers. If False, enemies are separated into individual layers.
    compress_enemies: bool

    #: bool: Encodes snake body segments using a one-hot representation to differentiate the order of body parts.
    include_snake_body_as_one_hot: bool

    #: bool: Includes a standard spatial layer showing the occupied positions of all snake bodies.
    include_snake_body: bool

    #: bool: Includes a specific spatial layer indicating the positions of snake heads.
    include_snake_head: bool

    #: bool: Includes a specific spatial layer indicating the positions of snake tails.
    include_snake_tail: bool

    #: bool: Includes a feature or layer representing the current health (starvation countdown) of the snakes.
    include_snake_health: bool

    #: bool: Includes a feature or layer representing the current length of the snakes.
    include_snake_length: bool

    #: bool: Includes a spatial distance map (e.g., Manhattan distance from the ego snake's head to other tiles).
    include_distance_map: bool

    #: bool: If True, flattens the multi-dimensional spatial tensor into a 1D array before returning.
    flatten: bool

    #: bool: Centers the spatial observation tensor around the ego snake's head (egocentric view) rather than using an absolute board (allocentric view).
    centered: bool

    #: bool: Includes a layer detailing area control metrics, such as a Voronoi partition showing which snake is closest to which tiles.
    include_area_control: bool

    #: bool: Includes a feature or gradient layer representing the distance to the nearest food item.
    include_food_distance: bool

    #: bool: Includes a spatial layer mapping hazard zones (e.g., the shrinking hazard sauce in Royale mode).
    include_hazards: bool

    #: bool: Includes a feature representing the distance from the ego snake's head to its own tail.
    include_tail_distance: bool

    #: bool: Includes a global feature representing the total number of food items currently spawned on the board.
    include_num_food_on_board: bool = False

    #: bool: Includes an environment temperature input feature, often used for modulating exploration or custom game modes.
    temperature_input: bool = False

    #: bool: If True, represents the temperature input as a single global scalar value.
    single_temperature_input: bool = True

    #: float: Sets a fixed probability for food spawning. A value of `-1` indicates that the default game rules for food spawn chance should be used.
    fixed_food_spawn_chance: float = -1.0

    #: bool: Includes a mask layer representing the limited field of view of the snake, useful for partially observable training environments.
    include_view_mask: bool = False


def num_layers_general(cfg: BattleSnakeEncodingConfig) -> int:
    result = (
        cfg.include_current_food
        + cfg.include_next_food
        + cfg.include_board
        + cfg.include_number_of_turns
        + cfg.include_distance_map
        + cfg.include_hazards
        + cfg.include_num_food_on_board
    )
    if cfg.temperature_input and cfg.single_temperature_input:
        result += 1
    return result


def layers_per_player(cfg: BattleSnakeEncodingConfig) -> int:
    result = (
        cfg.include_snake_body
        + cfg.include_snake_head
        + cfg.include_snake_tail
        + cfg.include_snake_health
        + cfg.include_snake_length
        + cfg.include_area_control
        + cfg.include_food_distance
        + cfg.include_tail_distance
        + cfg.include_snake_body_as_one_hot
    )
    return result


def layers_per_enemy(cfg: BattleSnakeEncodingConfig) -> int:
    result = layers_per_player(cfg)
    if cfg.temperature_input and not cfg.single_temperature_input:
        result += 1
    return result


# Standard Mode #####################################################
@dataclass
class SimpleBattleSnakeEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=True)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=False)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=False)
    include_snake_body: bool = field(default=True)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=False)
    include_snake_health: bool = field(default=False)
    include_snake_length: bool = field(default=False)
    include_distance_map: bool = field(default=False)
    flatten: bool = field(default=False)
    centered: bool = field(default=False)
    include_area_control: bool = field(default=False)
    include_food_distance: bool = field(default=False)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=False)
    include_num_food_on_board: bool = field(default=False)
    fixed_food_spawn_chance: float = field(default=-1)


@dataclass
class VanillaBattleSnakeEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=True)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=False)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=True)
    include_snake_body: bool = field(default=True)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=True)
    include_snake_health: bool = field(default=True)
    include_snake_length: bool = field(default=True)
    include_distance_map: bool = field(default=True)
    flatten: bool = field(default=False)
    centered: bool = field(default=True)
    include_area_control: bool = field(default=False)
    include_food_distance: bool = field(default=False)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=False)
    include_num_food_on_board: bool = field(default=False)
    fixed_food_spawn_chance: float = field(default=-1)


@dataclass
class BestBattleSnakeEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=True)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=False)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=True)
    include_snake_body: bool = field(default=True)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=True)
    include_snake_health: bool = field(default=True)
    include_snake_length: bool = field(default=True)
    include_distance_map: bool = field(default=True)
    flatten: bool = field(default=False)
    centered: bool = field(default=True)
    include_area_control: bool = field(default=True)
    include_food_distance: bool = field(default=True)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=True)
    include_num_food_on_board: bool = field(default=True)
    fixed_food_spawn_chance: float = field(default=-1)


# Constrictor Mode #####################################################
@dataclass
class SimpleConstrictorEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=False)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=False)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=True)
    include_snake_body: bool = field(default=False)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=False)
    include_snake_health: bool = field(default=False)
    include_snake_length: bool = field(default=False)
    include_distance_map: bool = field(default=False)
    flatten: bool = field(default=False)
    centered: bool = field(default=True)
    include_area_control: bool = field(default=False)
    include_food_distance: bool = field(default=False)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=False)
    include_num_food_on_board: bool = field(default=False)
    fixed_food_spawn_chance: float = field(default=-1)


@dataclass
class BestConstrictorEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=False)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=False)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=True)
    include_snake_body: bool = field(default=False)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=False)
    include_snake_health: bool = field(default=False)
    include_snake_length: bool = field(default=False)
    include_distance_map: bool = field(default=True)
    flatten: bool = field(default=False)
    centered: bool = field(default=True)
    include_area_control: bool = field(default=False)
    include_food_distance: bool = field(default=False)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=False)
    include_num_food_on_board: bool = field(default=False)
    fixed_food_spawn_chance: float = field(default=-1)


# Restricted Mode #####################################################
@dataclass
class BestRestrictedEncodingConfig(BattleSnakeEncodingConfig):
    include_current_food: bool = field(default=True)
    include_next_food: bool = field(default=False)
    include_board: bool = field(default=True)
    include_number_of_turns: bool = field(default=True)
    compress_enemies: bool = field(default=True)
    include_snake_body_as_one_hot: bool = field(default=True)
    include_snake_body: bool = field(default=True)
    include_snake_head: bool = field(default=True)
    include_snake_tail: bool = field(default=True)
    include_snake_health: bool = field(default=True)
    include_snake_length: bool = field(default=True)
    include_distance_map: bool = field(default=True)
    flatten: bool = field(default=False)
    centered: bool = field(default=True)
    include_area_control: bool = field(default=False)
    include_food_distance: bool = field(default=False)
    include_hazards: bool = field(default=False)
    include_tail_distance: bool = field(default=False)
    include_num_food_on_board: bool = field(default=False)
    fixed_food_spawn_chance: float = field(default=-1)
    include_view_mask: bool = field(default=True)
