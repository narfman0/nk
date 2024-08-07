"""Simulates the world's characters"""

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.map import Map
from nk_shared.models import AttackProfile, AttackType, Character, Zone
from nk_shared.proto import Message

from nk.ai_component import AiComponent
from nk.message_component import MessageComponent
from nk.models import Player, WorldComponentProvider
from nk.projectile_component import ProjectileComponent
from nk.settings import DATA_ROOT


class World(WorldComponentProvider):  # pylint: disable=too-many-instance-attributes
    """Hold and simulate everything happening in the game."""

    def __init__(self, zone_name: str = "1"):
        self._space = pymunk.Space()
        self._zone = Zone.from_yaml_file(f"{DATA_ROOT}/zones/{zone_name}.yml")
        self._map = Map(self._zone.tmx_path, pygame=False)
        self._map.add_map_geometry_to_space(self._space)
        self._players: list[Player] = []
        self._ai_component = AiComponent(self, self._zone)
        self._projectile_component = ProjectileComponent(self)
        self._message_component = MessageComponent(self)

    def update(self, dt: float):
        self._ai_component.update(dt)
        self.update_characters(dt, self._players, self._ai_component.enemies)
        self.update_characters(dt, self._ai_component.enemies, self._players)
        self._projectile_component.update(dt)
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
        projectile = self._projectile_component.create_projectile(character)
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

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        for character in self._players + self._ai_component.enemies:
            if character.uuid == uuid:
                return character
        return None

    async def handle_message(self, player: Player, msg: Message):
        await self._message_component.handle_message(player, msg)

    def broadcast(self, message: Message, origin: Player | None = None) -> None:
        for player in self._players:
            if player != origin:
                player.messages.put_nowait(message)

    async def handle_player_disconnected(self, player: Player):
        await self._message_component.handle_player_disconnected(player)

    @property
    def map(self) -> Map:
        return self._map

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def space(self) -> pymunk.Space:
        return self._space


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
