import numpy as np


def create_third_strategy_matrix(n):
    """
    Create a matrix for the third strategy where columns that are always used together in the workload queries are combined.

    Args:
    n (int): The number of columns in the original matrix, which should be even.

    Returns:
    numpy.ndarray: The resulting matrix for the third strategy.
    """
    if n % 2 != 0:
        raise ValueError("The number of columns should be even.")

    result = np.zeros((n // 2, n))
    for i in range(0, n, 2):
        result[i // 2, i] = 1
        result[i // 2, i + 1] = 1
    return result


# Example usage:
n = 10
third_strategy_matrix = create_third_strategy_matrix(n)
print(third_strategy_matrix)
