from enum import Enum
from math import atan2, pi

from pymunk import Vec2d

from nk_shared.proto import Direction


def to_vector(direction: Direction) -> Vec2d:
    # lrucacheable!
    return {
        Direction.N: Vec2d(0, -1),
        Direction.NE: Vec2d(1, -1),
        Direction.E: Vec2d(1, 0),
        Direction.SE: Vec2d(1, 1),
        Direction.S: Vec2d(0, 1),
        Direction.SW: Vec2d(-1, 1),
        Direction.W: Vec2d(-1, 0),
        Direction.NW: Vec2d(-1, -1),
    }[direction].normalized()


def to_isometric(direction: Direction):
    return {
        Direction.N: Direction.NE,
        Direction.NE: Direction.E,
        Direction.E: Direction.SE,
        Direction.SE: Direction.S,
        Direction.S: Direction.SW,
        Direction.SW: Direction.W,
        Direction.W: Direction.NW,
        Direction.NW: Direction.N,
    }[direction]


def direction_to(origin: Vec2d, target: Vec2d):
    """Get direction to position b from position a"""
    angle = atan2(target.y - origin.y, target.x - origin.x)
    angle += pi / 8  # this makes things a bit more concise
    if angle >= 0:
        if angle < pi / 4:
            result = Direction.E
        elif angle < pi / 2:
            result = Direction.SE
        elif angle < 3 * pi / 4:
            result = Direction.S
        else:
            result = Direction.SW
    else:
        if angle > -pi / 4:
            result = Direction.NE
        elif angle > -pi / 2:
            result = Direction.N
        elif angle > -3 * pi / 4:
            result = Direction.NW
        else:
            result = Direction.W
    return result


def angle(direction: Direction) -> float:
    vectorized = to_vector(direction)
    return atan2(vectorized.y, vectorized.x)
