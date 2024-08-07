"""Simulates the world's characters"""

from functools import lru_cache
from math import cos, sin
from os import environ
from uuid import uuid4

import pymunk
from betterproto import serialized_on_wire
from loguru import logger
from nk.projectile_component import ProjectileComponent
from nk_shared import builders
from nk_shared.map import Map
from nk_shared.models import AttackProfile, AttackType, Character, Projectile, Zone
from nk_shared.proto import (
    CharacterAttacked,
    CharacterUpdated,
    Direction,
    Message,
    PlayerJoined,
    PlayerJoinResponse,
    PlayerLeft,
)

from nk.ai_component import AiComponent
from nk.db import Character as DBCharacter
from nk.models import Enemy, Player, WorldComponentProvider

DATA_ROOT = environ.get("NK_DATA_ROOT", "../data")


class World(WorldComponentProvider):  # pylint: disable=too-many-instance-attributes
    """Hold and simulate everything happening in the game."""

    def __init__(self, zone_name: str = "1"):
        self.attack_profiles: dict[str, AttackProfile] = {}
        self._space = pymunk.Space()
        self.zone = Zone.from_yaml_file(f"{DATA_ROOT}/zones/{zone_name}.yml")
        self.map = Map(self.zone.tmx_path, pygame=False)
        self.map.add_map_geometry_to_space(self._space)
        self.players: list[Player] = []
        self.ai_component = AiComponent(self, self.zone)
        self.projectile_component = ProjectileComponent(self)

    def update(self, dt: float):
        self.ai_component.update(dt)
        self.update_characters(dt, self.players, self.ai_component.enemies)
        self.update_characters(dt, self.ai_component.enemies, self.players)
        self.projectile_component.update(dt)
        self._space.step(dt)

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
                self._space.remove(
                    character.body, character.shape, character.hitbox_shape
                )

    def process_ranged_attack(self, character: Character):
        attack_profile = self.get_attack_profile_by_name(character.attack_profile_name)
        # speed = direction_util.to_vector(character.facing_direction).scale_to_length(
        #     attack_profile.speed
        # )
        speed = pymunk.Vec2d(
            cos(character.attack_direction), sin(character.attack_direction)
        ).scale_to_length(attack_profile.speed)
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
        self.projectile_component.projectiles.append(projectile)
        self.broadcast(builders.build_projectile_created(projectile))
        character.should_process_attack = False
        logger.debug("Projectile created: {}", projectile.uuid)

    def process_attack_damage(self, attacker: Character, targets: list[Character]):
        """Attack trigger frame reached, let's find who was hit and apply dmg"""
        attacker.should_process_attack = False
        for target in targets:
            if attacker.hitbox_shape.shapes_collide(target.shape).points:
                damage = 1
                target.handle_damage_received(damage)
                self.broadcast(builders.build_character_damaged(target, damage))

    def handle_character_attacked(self, details: CharacterAttacked):
        """Call character attack, does nothing if character does not exist"""
        character = self.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: {}", details.uuid)
        logger.info(details)
        character.attack(details.direction)

    def handle_character_updated(self, details: CharacterUpdated):
        """Apply message details to relevant character. If character
        does not exist, do not do anything."""
        character = self.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: {}", details.uuid)
        character.body.position = (details.x, details.y)
        character.moving_direction = Direction(details.moving_direction)
        character.facing_direction = Direction(details.facing_direction)
        character.body.velocity = (details.dx, details.dy)

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        for character in self.players + self.ai_component.enemies:
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

    async def spawn_player(self, player: Player) -> Player:
        """Player 'is' a Character, which i don't love, but its already
        created. Update relevant attrs."""
        character = await DBCharacter.find_one(DBCharacter.user_id == player.uuid)
        if character:
            x, y = character.x, character.y
        else:
            x, y = world.map.get_start_tile()
        player.body.position = (x, y)
        self._space.add(player.body, player.shape, player.hitbox_shape)
        self.players.append(player)
        return player

    async def handle_player_disconnected(self, player: Player):
        self.broadcast(Message(player_left=PlayerLeft(uuid=player.uuid)), player)
        x, y = player.position.x, player.position.y  # pylint: disable=no-member
        character = await DBCharacter.find_one(DBCharacter.user_id == player.uuid)
        if character:
            await character.set({DBCharacter.x: x, DBCharacter.y: y})
        else:
            await DBCharacter(user_id=player.uuid, x=x, y=y).insert()
        logger.info("Successfully saved player post-logout")
        self.players.remove(player)

    async def handle_player_join_request(self, player: Player):
        """A player has joined. Handle initialization."""
        await self.spawn_player(player)
        logger.info("Join request success: {}", player.uuid)
        x, y = player.position.x, player.position.y
        response = PlayerJoinResponse(uuid=player.uuid, x=x, y=y)
        await player.messages.put(Message(player_join_response=response))
        self.broadcast(Message(player_joined=PlayerJoined(uuid=player.uuid)), player)

    async def handle_message(self, player: Player, msg: Message):
        """Socket-level handler for messages, mostly passing through to world"""
        if serialized_on_wire(msg.player_join_request):
            await self.handle_player_join_request(player)
        elif serialized_on_wire(msg.text_message):
            self.broadcast(msg, player)
        elif serialized_on_wire(msg.character_attacked):
            self.handle_character_attacked(msg.character_attacked)
        elif serialized_on_wire(msg.character_updated):
            self.handle_character_updated(msg.character_updated)
            self.broadcast(msg, player)

    def broadcast(self, message: Message, origin: Player | None = None) -> None:
        for player in self.players:
            if player != origin:
                player.messages.put_nowait(message)

    @property
    def space(self) -> pymunk.Space:
        return self._space

    @lru_cache
    def get_attack_profile_by_name(self, attack_profile_name: str) -> AttackProfile:
        path = f"{DATA_ROOT}/attack_profiles/{attack_profile_name}.yml"
        return AttackProfile.from_yaml_file(path)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
