from random import uniform

import numpy as np


def choice_weighted(weights: np.ndarray) -> int:
    """
    Precondition: the sum of all the weights should add up to 1.0
    :param weights: a list of floating point representing the probability of selecting each index.
    :return: a randomly selected index based off of weights.
    """
    selector = uniform(0, 1)
    result = 0
    while result < len(weights):
        selector -= weights[result]
        if selector <= 0:
            return result
        result += 1
    return len(weights) - 1
