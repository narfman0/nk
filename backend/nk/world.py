"""Simulates the world's characters"""

import logging
import random
from functools import lru_cache
from os import environ
from uuid import uuid4

import pymunk
from nk_shared import builders
from nk_shared.map import Map
from nk_shared.models import AttackProfile, AttackType, Character, Projectile, Zone
from nk_shared.proto import CharacterType, CharacterUpdated, Direction, Message
from nk_shared.util import direction_util

from nk.db import Character as DBCharacter
from nk.models import Enemy, Player

DATA_ROOT = environ.get("NK_DATA_ROOT", "../data")
UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


class World:  # pylint: disable=too-many-instance-attributes
    """Hold and simulate everything happening in the game."""

    def __init__(self, zone_name: str = "1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.zone = Zone.from_yaml_file(f"{DATA_ROOT}/zones/{zone_name}.yml")
        self.map = Map(self.zone.tmx_path, pygame=False)
        self.map.add_map_geometry_to_space(self.space)
        self.players: list[Player] = []
        self.enemies: list[Enemy] = []
        for enemy_group in self.zone.enemy_groups:
            r = 1 + enemy_group.count // 2  # randomize where group is centered
            for _ in range(enemy_group.count):
                self.spawn_enemy(
                    enemy_group.character_type,
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
        self.update_projectiles(dt)
        self.space.step(dt)

    def update_characters(
        self,
        dt: float,
        characters: list[Character],
        targets: list[Character],
    ):
        """Update given characters (players and enemies)"""
        for character in characters:
            character.update(dt)
            if character.should_process_attack:
                if character.attack_type == AttackType.MELEE:
                    self.process_attack_damage(character, targets)
                elif character.attack_type == AttackType.RANGED:
                    self.process_ranged_attack(character)
            if not character.alive and not character.body_removal_processed:
                character.body_removal_processed = True
                self.space.remove(
                    character.body, character.shape, character.hitbox_shape
                )

    def update_projectiles(self, dt: float):
        for projectile in self.projectiles:
            projectile.update(dt)
            should_remove = False
            for query_info in self.space.shape_query(projectile.shape):
                if hasattr(query_info.shape.body, "character"):
                    character: Character = query_info.shape.body.character
                    # i guess there's friendly fire for now :D
                    if projectile.origin != character:
                        dmg = 1
                        character.handle_damage_received(dmg)
                        self.broadcast(builders.build_character_damaged(character, dmg))
                        should_remove = True
                else:
                    should_remove = True
            if should_remove:
                self.projectiles.remove(projectile)
                self.broadcast(builders.build_projectile_destroyed(projectile.uuid))
                logger.debug("Projectile destroyed: %s", projectile.uuid)

    def process_ranged_attack(self, character: Character):
        attack_profile = self.get_attack_profile_by_name(character.attack_profile_name)
        speed = direction_util.to_vector(character.facing_direction).scale_to_length(
            attack_profile.speed
        )
        projectile = Projectile(
            x=character.position.x + attack_profile.emitter_offset_x,
            y=character.position.y + attack_profile.emitter_offset_y,
            dx=speed.x,
            dy=speed.y,
            origin=character,
            attack_profile=attack_profile,
            attack_profile_name=attack_profile.name,
            uuid=str(uuid4()),
        )
        self.projectiles.append(projectile)
        self.broadcast(builders.build_projectile_created(projectile))
        character.should_process_attack = False
        logger.debug("Projectile created: %s", projectile.uuid)

    def process_attack_damage(self, attacker: Character, targets: list[Character]):
        """Attack trigger frame reached, let's find who was hit and apply dmg"""
        attacker.should_process_attack = False
        for target in targets:
            if attacker.hitbox_shape.shapes_collide(target.shape).points:
                damage = 1
                target.handle_damage_received(damage)
                self.broadcast(builders.build_character_damaged(target, damage))

    def update_ai(self, dt: float):
        """Update enemy behaviors. Long term refactor option (e.g. behavior trees)"""
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                enemy.moving_direction = None
                player = self.closest_player(enemy.position.x, enemy.position.y)
                if not player:
                    continue
                player_dst_sqrd = enemy.position.get_dist_sqrd(player.position)
                if player_dst_sqrd < enemy.chase_distance**2:
                    enemy.moving_direction = direction_util.direction_to(
                        enemy.position, player.position
                    )
                if player_dst_sqrd < enemy.attack_distance**2 and not enemy.attacking:
                    enemy.attack()
                    self.broadcast(builders.build_character_attacked(enemy))
                self.broadcast(builders.build_character_updated(enemy))

    def handle_character_attacked(self, details: CharacterUpdated):
        """Call character attack, does nothing if character does not exist"""
        character = self.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: %s", details.uuid)
        logger.info(details)
        character.attack()

    def handle_character_updated(self, details: CharacterUpdated):
        """Apply message details to relevant character. If character
        does not exist, do not do anything."""
        character = self.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: %s", details.uuid)
        character.body.position = (details.x, details.y)
        character.moving_direction = Direction(details.moving_direction)
        character.facing_direction = Direction(details.facing_direction)

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        for character in self.players + self.enemies:
            if character.uuid == uuid:
                return character
        return None

    def closest_player(self, x: float, y: float) -> Player | None:
        """Retrieve the closest player to the given x,y pair.
        Long term, should considering splitting world into zone/chunks, but
        this is a scan currently."""
        closest, min_dst = None, float("inf")
        for player in self.players:
            if player.alive:
                dst = player.position.get_dist_sqrd((x, y))
                if dst < min_dst:
                    closest = player
                    min_dst = dst
        return closest

    def spawn_enemy(
        self, character_type: CharacterType, center_x: int, center_y: int
    ) -> Enemy:
        character = Enemy(
            character_type=character_type,
            center_y=center_y,
            center_x=center_x,
            start_x=center_x,
            start_y=center_y,
        )
        self.space.add(character.body, character.shape, character.hitbox_shape)
        self.enemies.append(character)
        return character

    async def spawn_player(self, player: Player) -> Player:
        """Player 'is' a Character, which i don't love, but its already
        created. Update relevant attrs."""
        character = await DBCharacter.find_one(DBCharacter.user_id == player.uuid)
        if character:
            x, y = character.x, character.y
        else:
            x, y = world.map.get_start_tile()
        player.body.position = (x, y)
        self.space.add(player.body, player.shape, player.hitbox_shape)
        self.players.append(player)
        return player

    def broadcast(self, message: Message):
        for player in self.players:
            player.messages.put_nowait(message)

    @lru_cache
    def get_attack_profile_by_name(self, attack_profile_name: str) -> AttackProfile:
        path = f"{DATA_ROOT}/attack_profiles/{attack_profile_name}.yml"
        return AttackProfile.from_yaml_file(path)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
