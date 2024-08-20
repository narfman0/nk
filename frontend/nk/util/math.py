from functools import lru_cache


@lru_cache(maxsize=128)
def cartesian_to_isometric(
    cartesian_x: float, cartesian_y: float
) -> tuple[float, float]:
    return cartesian_x - cartesian_y, (cartesian_x + cartesian_y) // 2


def isometric_to_cartesian(
    isometric_x: float, isometric_y: float
) -> tuple[float, float]:
    return (2 * isometric_y + isometric_x) / 2, (2 * isometric_y - isometric_x) / 2
