from enum import Enum
from math import atan2, pi

from pymunk import Vec2d


class Direction(Enum):
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8

    def to_vector(self) -> Vec2d:
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
        }[self].normalized()

    def to_isometric(self):
        return {
            Direction.N: Direction.NE,
            Direction.NE: Direction.E,
            Direction.E: Direction.SE,
            Direction.SE: Direction.S,
            Direction.S: Direction.SW,
            Direction.SW: Direction.W,
            Direction.W: Direction.NW,
            Direction.NW: Direction.N,
        }[self]

    @classmethod
    def direction_to(cls, origin: Vec2d, target: Vec2d):
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

    @property
    def angle(self) -> float:
        vectorized = self.to_vector()
        return atan2(vectorized.y, vectorized.x)
