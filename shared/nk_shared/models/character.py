from dataclasses import dataclass, field
from uuid import UUID, uuid4 as generate_uuid

import pymunk

from nk_shared.models.character_properties import CharacterProperties
from nk_shared.proto import CharacterType, Direction
from nk_shared.util import direction_util


@dataclass
class Character(CharacterProperties):
    character_type: CharacterType = CharacterType.CHARACTER_TYPE_PIGSASSIN
    uuid: UUID = field(default_factory=generate_uuid)
    facing_direction: Direction = Direction.DIRECTION_S
    moving_direction: Direction = None
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
    hp: float = 0
    invincible: bool = False
    body_removal_processed: bool = False
    start_x: float = 0
    start_y: float = 0

    def __post_init__(self):
        self.apply_character_properties()
        self.hp = float(self.hp_max)
        self.body = pymunk.Body()
        self.body.position = self.start_x, self.start_y
        self.body.character = self
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.mass = self.mass
        self.hitbox_shape = pymunk.Segment(
            self.body, (0, 0), (self.attack_distance, 0), radius=1
        )
        self.hitbox_shape.sensor = True

    def handle_damage_received(self, dmg: float):
        if not self.invincible:
            self.hp = max(0, self.hp - dmg)
            if not self.alive:
                self.body._set_type(pymunk.Body.STATIC)

    def handle_healing_received(self, amount: float):
        self.hp = min(self.hp_max, self.hp + amount)
        if self.alive:
            self.body._set_type(pymunk.Body.DYNAMIC)

    def update(self, dt: float):
        if self.alive and self.moving_direction:
            self.facing_direction = self.moving_direction
            self.body.angle = direction_util.angle(self.facing_direction)
            dash_scalar = self.dash_scalar if self.dashing else 1.0
            dpos = (
                direction_util.to_vector(self.moving_direction)
                * self.run_force
                * dash_scalar
                * dt
            )
            self.body.apply_force_at_world_point(
                force=(dpos.x, dpos.y), point=(self.position.x, self.position.y)
            )
            if self.body.velocity.length > self.max_velocity * dash_scalar:
                self.body.velocity = self.body.velocity.scale_to_length(
                    self.max_velocity * dash_scalar
                )
        else:
            if self.body.velocity.get_length_sqrd() > self.running_stop_threshold:
                self.body.velocity = self.body.velocity.scale_to_length(
                    0.7 * self.body.velocity.length
                )
            else:
                self.body.velocity = (0, 0)
        if not self.alive:
            return
        if self.dashing:
            self.dash_time_remaining -= dt
            if self.dash_time_remaining <= 0:
                self.dashing = 0
                self.dash_time_remaining = 0
                self.dash_cooldown_remaining = self.dash_cooldown
        elif self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= dt
            if self.dash_cooldown_remaining <= 0:
                self.dash_cooldown_remaining = 0

        if self.attacking:
            self.attack_time_remaining -= dt
            if self.attack_damage_time_remaining > 0:
                self.attack_damage_time_remaining -= dt
                if self.attack_damage_time_remaining <= 0:
                    self.attack_damage_time_remaining = 0
                    self.should_process_attack = True
            if self.attack_time_remaining <= 0:
                self.attacking = False

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_time_remaining = self.attack_duration
            self.attack_damage_time_remaining = self.attack_time_until_damage
            if self.moving_direction:  # maybe standing still
                self.facing_direction = self.moving_direction

    def dash(self):
        if not self.dashing and self.dash_cooldown_remaining <= 0:
            self.dashing = True
            self.dash_time_remaining = self.dash_duration

    def apply_character_properties(self):
        path = f"../data/characters/{self.character_type_short}/character.yml"
        character_properties = CharacterProperties.from_yaml_file(path)
        self.__dict__.update(character_properties.__dict__)

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def character_type_short(self):
        return self.character_type.name.lower()[15:]
