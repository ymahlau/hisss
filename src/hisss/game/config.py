from dataclasses import dataclass, field
from typing import Optional

from hisss.game.encoding import BattleSnakeEncodingConfig, BestBattleSnakeEncodingConfig, BestRestrictedEncodingConfig, SimpleBattleSnakeEncodingConfig, VanillaBattleSnakeEncodingConfig
from hisss.game.rewards import BattleSnakeRewardConfig, KillBattleSnakeRewardConfig, StandardBattleSnakeRewardConfig


@dataclass
class BattleSnakeConfig:
    num_actions: int = field(default=4)
    num_players: int = field(default=2)
    # board
    w: int = 5
    h: int = 5
    # encoding
    ec: BattleSnakeEncodingConfig = field(default_factory=SimpleBattleSnakeEncodingConfig)
    # snakes
    all_actions_legal: bool = False
    max_snake_health: Optional[list[int]] = None
    # food
    min_food: int = 1
    food_spawn_chance: int = 15
    # game state initialization
    init_turns_played: int = 0
    init_snakes_alive: Optional[list[bool]] = None  # if this is None, all snakes are alive
    init_snake_pos: Optional[dict[int, list[list[int]]]] = None  # if this is None, snakes spawn randomly
    init_food_pos: Optional[list[list[int]]] = None  # if None spawn food randomly, if [] spawn no food
    init_snake_health: Optional[list[int]] = None
    init_snake_len: Optional[list[int]] = None
    # rewards
    reward_cfg: BattleSnakeRewardConfig = field(default_factory=StandardBattleSnakeRewardConfig)
    # special game modes
    wrapped: bool = False
    royale: bool = False
    constrictor: bool = False
    shrink_n_turns: int = 25
    hazard_damage: int = 14
    init_hazards: Optional[list[list[int]]] = None
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
            assert cfg.init_snake_pos is not None, "You cannot spawn snakes randomly and food fixed"
    if cfg.init_snake_pos is not None:
        assert len(cfg.init_snake_pos) == cfg.num_players
        assert cfg.init_food_pos is not None, "You cannot spawn snakes fixed and food randomly"
    if cfg.w != cfg.h or cfg.w % 2 == 0 or cfg.h % 2 == 0:
        assert cfg.init_snake_pos is not None, "Cannot spawn snakes randomly on weird board shapes"
        assert cfg.init_food_pos is not None, "Cannot spawn food randomly on weird board shapes"
    # health, lengths, turns
    assert len(cfg.init_snake_health) == cfg.num_players
    for i in range(cfg.num_players):
        assert cfg.max_snake_health[i] >= cfg.init_snake_health[i]
    assert len(cfg.max_snake_health) == cfg.num_players
    assert len(cfg.init_snake_len) == cfg.num_players
    assert cfg.init_turns_played >= 0
    # game modes
    if cfg.w != cfg.h or cfg.w % 2 != 1:
        assert not cfg.ec.centered, "Can only center observation in odd-sized square boards"
    if cfg.wrapped:
        assert not cfg.ec.include_board, "You do not want to include borders in wrapped mode"
    if cfg.royale:
        assert cfg.w == cfg.h, "Royale Mode only works with square boards"
    if cfg.constrictor:
        assert len(cfg.init_hazards) == 0, "Constrictor does not work with hazards"
        assert not cfg.royale, "Constrictor does not work with royale"
    if cfg.view_radius is not None:
        assert cfg.ec.include_distance_map, "Restricted mode needs distance map to calculate observation mask"
        assert not cfg.ec.include_area_control, "Restricted mode cannot use area control in observations"
        assert not cfg.ec.include_food_distance, "Restricted mode cannot use food distance in observations"
        assert not cfg.ec.include_num_food_on_board, "Restricted mode cannot use number of food on the board in obs"
    if cfg.ec.include_view_mask:
        assert cfg.view_radius is not None, "Can only include view mask in obs if view_radius is set in game config"


def encoding_layer_indices(game_cfg: BattleSnakeConfig) -> dict[str, int]:
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
        res_dict[f"view_mask"] = layer_counter
        layer_counter += 1
    return res_dict


def duel_config() -> BattleSnakeConfig:
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
