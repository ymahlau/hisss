import numpy as np

from hisss.cpp.lib import CPP_LIB


def calculate_nash_equilibrium(
    available_actions: list[
        list[int]
    ],  # maps player(index of player_at_turn) to available actions
    joint_action_list: list[tuple[int, ...]],
    joint_action_value_arr: np.ndarray,  # shape (num_joint_actions, num_player_at_turn)
) -> tuple[list[float], list[np.ndarray]]:
    """
    Calculates the Nash equilibrium for a given game formulation using a C++ backend.
    The algorithm used here is from Porter et al. ("Simple search methods for finding a Nash equilibrium").
    It works for both 2-player as well as N-player games.

    Args:
        available_actions (list[list[int]]): A list where the index represents the player
            and the value is a list of integer IDs representing their available actions.
        joint_action_list (list[tuple[int, ...]]): A list of all possible joint actions,
            where each tuple represents a combination of actions chosen by all players.
        joint_action_value_arr (np.ndarray): A 2D numpy array of shape
            (num_joint_actions, num_players) representing the payoffs. Rows correspond
            to the joint actions (aligned with `joint_action_list`) and columns
            correspond to each player's payout.

    Returns:
        tuple[list[float], list[np.ndarray]]: A tuple containing two elements:
            - value_list (list[float]): The expected payoff/value for each player at the
              calculated Nash equilibrium.
            - policy_list (list[np.ndarray]): The equilibrium strategy for each player,
              represented as a list of numpy arrays. Each array contains the probability
              distribution over that player's available actions.

    Raises:
        ValueError: If the number of columns in `joint_action_value_arr` does not
            match the number of players inferred from `available_actions`.
    """
    num_players = len(available_actions)
    if joint_action_value_arr.shape[1] != num_players:
        raise ValueError(f"Invalid array shape: {joint_action_value_arr.shape}")
    value_list, policy_list = CPP_LIB.compute_nash(
        available_actions=available_actions,
        joint_action_list=joint_action_list,
        joint_action_value_arr=joint_action_value_arr,
        error_counter=None,
    )
    return value_list, policy_list
