from functools import lru_cache


@lru_cache(maxsize=128)
def cartesian_to_isometric(
    cartesian_x: float, cartesian_y: float
) -> tuple[float, float]:
    return cartesian_x - cartesian_y, (cartesian_x + cartesian_y) // 2


def isometric_to_cartesian(
    isometric_x: float, isometric_y: float
) -> tuple[float, float]:
    cartesian_x = (isometric_x + isometric_y * 2) // 2
    return cartesian_x, cartesian_x + isometric_x
