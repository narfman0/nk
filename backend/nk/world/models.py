from asyncio import Queue
from dataclasses import dataclass
from enum import Enum
from math import atan2, pi
from uuid import UUID

import pymunk
from pymunk import Vec2d
from dataclass_wizard import YAMLWizard

from nk.proto import Message


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


@dataclass
class CharacterProperties(YAMLWizard):
    mass: float = 10
    run_force: float = 1000
    running_stop_threshold: float = 1.0
    max_velocity: float = 1
    radius: float = 0.5
    attack_duration: float = None
    attack_distance: float = None
    attack_time_until_damage: float = None
    attack_profile_name: str = None
    hp_max: int = 1
    chase_distance: float = 15


@dataclass
class Character(CharacterProperties):
    uuid: UUID | None = None
    facing_direction: Direction = Direction.S
    movement_direction: Direction = None
    shape: pymunk.Shape = None
    body: pymunk.Body = None
    hitbox_shape: pymunk.Shape = None
    dashing: bool = False
    dash_time_remaining: float = 0
    dash_cooldown_remaining: float = 0
    attacking: bool = False
    attack_time_remaining: float = 0
    attack_damage_time_remaining: float = 0
    should_process_attack: bool = False
    character_type: str = "pigsassin"
    hp: int = 1
    invincible: bool = False

    def __post_init__(self):
        self.apply_character_properties()
        self.hp = self.hp_max
        self.body = pymunk.Body()
        self.body.character = self
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.mass = self.mass
        self.hitbox_shape = pymunk.Segment(
            self.body, (0, 0), (self.attack_distance, 0), radius=1
        )
        self.hitbox_shape.sensor = True

    def apply_character_properties(self):
        path = f"../data/characters/{self.character_type}/character.yml"
        character_properties = CharacterProperties.from_yaml_file(path)
        self.__dict__.update(character_properties.__dict__)


@dataclass
class Player(Character):
    messages: Queue[Message] = Queue()
