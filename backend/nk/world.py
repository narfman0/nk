import logging
import random

import pymunk

from nk_shared import builders
from nk_shared.models import (
    AttackProfile,
    Character,
    Zone,
    Projectile,
)
from nk_shared.map import Map
from nk_shared.proto import CharacterType, CharacterUpdated
from nk_shared.util import direction_util

from nk.models import Enemy, Player

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


class World:

    def __init__(self, zone_name: str = "1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.zone = Zone.from_yaml_file(f"../data/zones/{zone_name}.yml")
        self.map = Map(self.zone.tmx_path, pygame=False)
        self.map.add_map_geometry_to_space(self.space)
        self.players: list[Player] = []
        self.enemies: list[Enemy] = []
        for enemy_group in self.zone.enemy_groups:
            r = 1 + enemy_group.count // 2  # randomize where group is centered
            for _ in range(enemy_group.count):
                self.spawn_enemy(
                    CharacterType[enemy_group.character_type.upper()],
                    enemy_group.center_x + random.randint(-r, r),
                    enemy_group.center_y + random.randint(-r, r),
                )
        self.next_update_time = 0

    def get_players(self) -> list[Player]:
        return self.players

    def update(self, dt: float):
        self.update_ai(dt)
        self.update_characters(dt, self.players, self.enemies)
        self.update_characters(dt, self.enemies, self.players)
        self.space.step(dt)

    def update_characters(
        self,
        dt: float,
        characters: list[Character],
        enemies: list[Character],
    ):
        for character in characters:
            character.update(dt)
            if character.should_process_attack:
                self.process_attack_damage(character, enemies)
            if not character.alive and not character.body_removal_processed:
                character.body_removal_processed = True
                self.space.remove(
                    character.body, character.shape, character.hitbox_shape
                )

    def process_attack_damage(self, attacker: Character, enemies: list[Character]):
        attacker.should_process_attack = False
        for enemy in enemies:
            if attacker.hitbox_shape.shapes_collide(enemy.shape).points:
                damage = 1  # TODO different dmg amounts
                enemy.handle_damage_received(damage)
                msg = builders.build_character_damaged(enemy, damage)
                for player in self.players:
                    player.messages.put_nowait(msg)

    def update_ai(self, dt: float):
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                player = self.closest_player(enemy.position.x, enemy.position.y)
                if not player:
                    continue
                enemy.moving_direction = None
                player_dst_sqrd = enemy.position.get_dist_sqrd(player.position)
                if player_dst_sqrd < enemy.chase_distance**2:
                    enemy.moving_direction = direction_util.direction_to(
                        enemy.position, player.position
                    )
                if player_dst_sqrd < enemy.attack_distance**2 and not enemy.attacking:
                    enemy.attack()
                    msg = builders.build_character_attacked(enemy)
                    for player in self.players:
                        player.messages.put_nowait(msg)
                msg = builders.build_character_updated(enemy)
                for player in self.players:
                    player.messages.put_nowait(msg)

    def handle_character_update(self, character_updated: CharacterUpdated):
        for character in self.players + self.enemies:
            if str(character.uuid) == character_updated.uuid:
                character.body.position = (character_updated.x, character_updated.y)
                character.moving_direction = character_updated.moving_direction
                character.facing_direction = character_updated.facing_direction

    def closest_player(self, x: float, y: float) -> Player | None:
        closest, min_dst = None, float("inf")
        for player in self.players:
            if player.alive:
                dst = player.position.get_dist_sqrd((x, y))
                if dst < min_dst:
                    closest = player
                    min_dst = dst
        return closest

    def spawn_enemy(self, character_type: CharacterType, center_x: int, center_y: int):
        enemy = Enemy(
            character_type=character_type,
            center_y=center_y,
            center_x=center_x,
            start_x=center_x,
            start_y=center_y,
        )
        self.space.add(enemy.body, enemy.shape, enemy.hitbox_shape)
        self.enemies.append(enemy)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
