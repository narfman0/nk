import logging
import random
from math import sin, cos

import pymunk

from nk_shared.builders import build_character_update_from_character
from nk_shared.models import Character, Level, AttackProfile, Projectile
from nk_shared.proto import CharacterType
from nk_shared.map import Map

from nk.models import Player

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


class World:

    def __init__(self, level_name: str = "1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.level = Level.from_yaml_file(f"../data/levels/{level_name}.yml")
        self.map = Map(self.level.tmx_path, pygame=False)
        self.map.add_map_geometry_to_space(self.space)
        self.players: list[Player] = []
        self.enemies: list[Character] = []
        for _i in range(5):
            pos = (20 + random.randint(-3, 3), 27 + random.randint(-3, 3))
            enemy = Character(
                position=pos, character_type=CharacterType.PIGSASSIN.name.lower()
            )
            self.space.add(enemy.body, enemy.shape, enemy.hitbox_shape)
            enemy.temp_center = pos  # we'll remove this eventually
            self.enemies.append(enemy)
        self.i = 0.0
        self.next_update_time = 0.0

    def get_players(self) -> list[Player]:
        return self.players

    def update(self, dt: float):
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            self.i += UPDATE_FREQUENCY
            for enemy in self.enemies:
                x, y = enemy.temp_center
                x += sin(self.i / 5) * 2
                y += cos(self.i / 5) * 2
                enemy.body.position = (x, y)
                msg = build_character_update_from_character(enemy)
                for player in self.players:
                    player.messages.put_nowait(msg)
        self.space.step(dt)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
