from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class BattleSnakeRewardType(Enum):
    """Enumeration of available BattleSnake reward function types."""

    STANDARD = "STANDARD"
    KILL = "KILL"
    COOP = "COOP"


@dataclass
class BattleSnakeRewardConfig:
    """Base configuration class for BattleSnake reward functions."""

    #: The reward given to a snake for surviving a turn.
    living_reward: float = 0.0
    #: The base reward given/taken when a snake wins/dies.
    terminal_reward: float = 1.0


class BattleSnakeRewardFunction(ABC):
    """Abstract base class for BattleSnake reward functions.

    Attributes:
        cfg (BattleSnakeRewardConfig): The configuration governing this reward function.
    """

    def __init__(self, cfg: BattleSnakeRewardConfig):
        self.cfg = cfg

    @abstractmethod
    def __call__(
        self,
        is_terminal: bool,
        num_players: int,
        players_at_turn: list[int],
        players_at_turn_last: list[int],
    ) -> np.ndarray:
        raise NotImplementedError()


@dataclass
class StandardBattleSnakeRewardConfig(BattleSnakeRewardConfig):
    """Configuration for the Standard BattleSnake reward function.

    Assigns a negative terminal reward to players who died this turn. The last
    remaining player receives a positive terminal reward. Surviving players receive
    a constant living reward (if configured) while the game is ongoing.
    """

    pass


class BattleSnakeRewardFunctionStandard(BattleSnakeRewardFunction):
    """Standard reward function for BattleSnake.

    Assigns a negative terminal reward to players who died this turn. The last
    remaining player receives a positive terminal reward. Surviving players receive
    a constant living reward (if configured) while the game is ongoing.
    """

    def __init__(self, cfg: StandardBattleSnakeRewardConfig):
        super().__init__(cfg)
        self.cfg = cfg

    def __call__(
        self,
        is_terminal: bool,
        num_players: int,
        players_at_turn: list[int],
        players_at_turn_last: list[int],
    ) -> np.ndarray:
        rewards = np.zeros(shape=(num_players,), dtype=float)
        num_at_turn = len(players_at_turn)
        # if everyone died, then nobody gets any reward
        if num_at_turn == 0:
            return rewards
        player_died = set(players_at_turn_last) - set(players_at_turn)
        # all players that died this round get a negative terminal reward
        for player in player_died:
            rewards[player] = -self.cfg.terminal_reward
        # last player alive gets positive reward
        if num_at_turn == 1:
            rewards[players_at_turn[0]] = self.cfg.terminal_reward
            return rewards
        # if game has not ended, all player alive get the living reward
        for (
            player
        ) in players_at_turn:  # all players still alive get a positive living reward
            rewards[player] = self.cfg.living_reward
        return rewards


@dataclass
class KillBattleSnakeRewardConfig(BattleSnakeRewardConfig):
    """Configuration for the Kill-based BattleSnake reward function.

    This reward function acts as a zero-sum or monotone game where cumulative
    un-discounted rewards balance out:
    - 2 players alive: zero-sum game around cum_reward of 2/3
    - 3 players alive: monotone game around cum_reward of 1/3 (kill reward is 1/3)
    - 4 players alive: monotone game around starting point of zero
    """

    pass


class BattleSnakeRewardFunctionKill(BattleSnakeRewardFunction):
    """Reward function that assigns fractional rewards when enemies are killed.

    This reward function acts as a zero-sum or monotone game where cumulative
    un-discounted rewards balance out:
    - 2 players alive: zero-sum game around cum_reward of 2/3
    - 3 players alive: monotone game around cum_reward of 1/3 (kill reward is 1/3)
    - 4 players alive: monotone game around starting point of zero
    """

    def __init__(self, cfg: KillBattleSnakeRewardConfig):
        super().__init__(cfg)
        self.cfg = cfg
        if self.cfg.living_reward != 0:
            raise ValueError(
                "Kill reward function does not work with living reward due to fixed maximum reward"
            )
        if self.cfg.terminal_reward != 1:
            raise ValueError("Need terminal reward on one for kill reward function")

    def __call__(
        self,
        is_terminal: bool,
        num_players: int,
        players_at_turn: list[int],
        players_at_turn_last: list[int],
    ) -> np.ndarray:
        # rewards still need to be scaled between -1 and 1. Technically max reward is 3 if all enemies kill themselves
        # in the same move, but we clip this rare situation
        rewards = np.zeros(shape=(num_players,), dtype=float)
        num_at_turn = len(players_at_turn)
        num_at_turn_last = len(players_at_turn_last)
        player_died = set(players_at_turn_last) - set(players_at_turn)
        # if everyone died, then nobody gets any reward
        if num_at_turn == 0:
            return rewards
        # if no one died, then no one gets any reward
        if len(player_died) == 0:
            return rewards
        # reward of dead players depends on number of dead players in last round
        for player in player_died:
            if num_at_turn_last == 4 and num_at_turn == 3:
                rewards[player] = -1
            elif num_at_turn_last == 4 and num_at_turn == 2:
                rewards[player] = -2 / 3
            elif num_at_turn_last == 4 and num_at_turn == 1:
                rewards[player] = -1 / 3
            elif num_at_turn_last == 3 and num_at_turn == 2:
                rewards[player] = -2 / 3
            elif num_at_turn_last == 3 and num_at_turn == 1:
                rewards[player] = -1 / 3
            elif num_at_turn_last == 2 and num_at_turn == 1:
                rewards[player] = -1 / 3
        # reward of players that are still alive
        for player in players_at_turn:
            if num_at_turn_last == 4 and num_at_turn == 3:
                rewards[player] = 1 / 3
            elif num_at_turn_last == 4 and num_at_turn == 2:
                rewards[player] = 2 / 3
            elif num_at_turn_last == 4 and num_at_turn == 1:
                rewards[player] = 1
            elif num_at_turn_last == 3 and num_at_turn == 2:
                rewards[player] = 1 / 3
            elif num_at_turn_last == 3 and num_at_turn == 1:
                rewards[player] = 2 / 3
            elif num_at_turn_last == 2 and num_at_turn == 1:
                rewards[player] = 1 / 3
        return rewards


@dataclass
class CooperationBattleSnakeRewardConfig(BattleSnakeRewardConfig):
    """Configuration for the Cooperation BattleSnake reward function.

    Defaults to providing a small living reward and a negative terminal reward
    when a snake dies.
    """

    living_reward: float = field(default=0.02)
    terminal_reward: float = -0.25


class BattleSnakeRewardFunctionCooperation(BattleSnakeRewardFunction):
    def __init__(self, cfg: CooperationBattleSnakeRewardConfig):
        super().__init__(cfg)
        self.cfg = cfg

    def __call__(
        self,
        is_terminal: bool,
        num_players: int,
        players_at_turn: list[int],
        players_at_turn_last: list[int],
    ) -> np.ndarray:
        num_at_turn = len(players_at_turn)
        num_at_turn_last = len(players_at_turn_last)
        num_dead = num_at_turn_last - num_at_turn
        # all players get negative terminal reward if a snake died
        rewards = np.zeros(shape=(num_players,), dtype=float)
        player_died = [p for p in players_at_turn_last if p not in players_at_turn]
        for p in player_died:
            rewards[p] += self.cfg.terminal_reward * num_at_turn_last
        for p in players_at_turn:
            rewards[p] += self.cfg.terminal_reward * num_dead
            rewards[p] += self.cfg.living_reward
        return rewards


def get_battlesnake_reward_func_from_cfg(
    cfg: BattleSnakeRewardConfig,
) -> BattleSnakeRewardFunction:
    if isinstance(cfg, StandardBattleSnakeRewardConfig):
        return BattleSnakeRewardFunctionStandard(cfg)
    elif isinstance(cfg, KillBattleSnakeRewardConfig):
        return BattleSnakeRewardFunctionKill(cfg)
    elif isinstance(cfg, CooperationBattleSnakeRewardConfig):
        return BattleSnakeRewardFunctionCooperation(cfg)
    else:
        raise ValueError(f"Unknown reward function type: {cfg}")
