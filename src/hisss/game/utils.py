import math
import numpy as np

def int_to_perm(
        seed: int,
        n: int,
) -> np.ndarray:
    """
    Uniquely maps integer to a permutation. The seed has to be less than n!
    Args:
        seed (): permutation seed
        n (): number of items
    Returns: permutation
    """
    lst = list(range(n))
    res = []
    m = n
    while len(res) < n:
        idx = seed % m
        item = lst.pop(idx)
        res.append(item)
        seed = math.floor(seed / m)
        m -= 1
    return np.asarray(res, dtype=np.int32)