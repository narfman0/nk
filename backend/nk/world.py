import logging
import random
from math import sin, cos

import pymunk

from nk_shared.builders import build_character_update_from_character
from nk_shared.models import Level, AttackProfile, Projectile
from nk_shared.map import Map

from nk.models import NPC, Player

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
        self.enemies: list[NPC] = []
        for enemy_group in self.level.enemy_groups:
            for _ in range(enemy_group.count):
                self.spawn_enemy(
                    enemy_group.character_type,
                    enemy_group.center_x + random.randint(-3, 3),
                    enemy_group.center_y + random.randint(-3, 3),
                )
        self.i = 0.0
        self.next_update_time = 0

    def get_players(self) -> list[Player]:
        return self.players

    def update(self, dt: float):
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            self.i += UPDATE_FREQUENCY
            for enemy in self.enemies:
                x, y = enemy.center_x, enemy.center_y
                x += sin(self.i / 5) * 2
                y += cos(self.i / 5) * 2
                enemy.body.position = (x, y)
                msg = build_character_update_from_character(enemy)
                for player in self.players:
                    player.messages.put_nowait(msg)
        self.space.step(dt)

    def spawn_enemy(self, character_type: str, center_x: int, center_y: int):
        enemy = NPC(
            character_type=character_type,
            center_y=center_y,
            center_x=center_x,
        )
        enemy.body.position = (center_x, center_y)
        self.space.add(enemy.body, enemy.shape, enemy.hitbox_shape)
        self.enemies.append(enemy)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
