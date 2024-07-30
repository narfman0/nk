from math import atan2, pi
from functools import cache

from pymunk import Vec2d

from nk_shared.proto import Direction


@cache
def to_vector(direction: Direction) -> Vec2d:
    return {
        Direction.DIRECTION_N: Vec2d(0, -1),
        Direction.DIRECTION_NE: Vec2d(1, -1),
        Direction.DIRECTION_E: Vec2d(1, 0),
        Direction.DIRECTION_SE: Vec2d(1, 1),
        Direction.DIRECTION_S: Vec2d(0, 1),
        Direction.DIRECTION_SW: Vec2d(-1, 1),
        Direction.DIRECTION_W: Vec2d(-1, 0),
        Direction.DIRECTION_NW: Vec2d(-1, -1),
    }[direction].normalized()


@cache
def to_isometric(direction: Direction):
    return {
        Direction.DIRECTION_N: Direction.DIRECTION_NE,
        Direction.DIRECTION_NE: Direction.DIRECTION_E,
        Direction.DIRECTION_E: Direction.DIRECTION_SE,
        Direction.DIRECTION_SE: Direction.DIRECTION_S,
        Direction.DIRECTION_S: Direction.DIRECTION_SW,
        Direction.DIRECTION_SW: Direction.DIRECTION_W,
        Direction.DIRECTION_W: Direction.DIRECTION_NW,
        Direction.DIRECTION_NW: Direction.DIRECTION_N,
    }[direction]


def direction_to(origin: Vec2d, target: Vec2d):
    """Get direction to position b from position a"""
    angle = atan2(target.y - origin.y, target.x - origin.x)
    angle += pi / 8  # this makes things a bit more concise
    if angle >= 0:
        if angle < pi / 4:
            result = Direction.DIRECTION_E
        elif angle < pi / 2:
            result = Direction.DIRECTION_SE
        elif angle < 3 * pi / 4:
            result = Direction.DIRECTION_S
        else:
            result = Direction.DIRECTION_SW
    else:
        if angle > -pi / 4:
            result = Direction.DIRECTION_NE
        elif angle > -pi / 2:
            result = Direction.DIRECTION_N
        elif angle > -3 * pi / 4:
            result = Direction.DIRECTION_NW
        else:
            result = Direction.DIRECTION_W
    return result


@cache
def angle(direction: Direction) -> float:
    vectorized = to_vector(direction)
    return atan2(vectorized.y, vectorized.x)
