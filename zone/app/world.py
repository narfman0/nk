"""Simulates the world's characters"""

from collections import deque

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.map import Map
from nk_shared.models import AttackType, Character, Zone
from nk_shared.proto import Message

from app.ai import Ai
from app.medical_manager import MedicalManager
from app.messages.handler import MessageHandler
from app.models import Enemy, Player, WorldComponentProvider, WorldListener
from app.projectile_manager import ProjectileManager
from app.pubsub import publish
from app.settings import DATA_ROOT


class World(WorldComponentProvider):  # pylint: disable=too-many-instance-attributes
    """Hold and simulate everything happening in the game."""

    def __init__(self, zone_name: str = "1"):
        self._listeners: deque[WorldListener] = deque()
        self._space = pymunk.Space()
        self._zone = Zone.from_yaml_file(f"{DATA_ROOT}/zones/{zone_name}.yml")
        self._map = Map(self._zone.tmx_path, headless=True)
        self._map.add_map_geometry_to_space(self._space)
        self._players: list[Player] = []
        self._ai = Ai(self, self._zone)
        self._projectile_component = ProjectileManager(self)
        self._message_handler = MessageHandler(self, self._ai)
        self._medical_manager = MedicalManager(self, self._zone.medics)

    async def update(self, dt: float):
        await self._ai.update(dt)
        await self.update_characters(dt, self._players, self._ai.enemies)
        await self.update_characters(dt, self._ai.enemies, self._players)
        await self._medical_manager.update(dt)
        await self._projectile_component.update(dt)
        self._space.step(dt)

    async def update_characters(
        self,
        dt: float,
        characters: list[Character],
        targets: list[Character],
    ):
        """Update given characters (players and enemies)"""
        for character in characters:
            character.update(dt)
            if character.should_process_attack:
                if character.weapon.attack_type == AttackType.MELEE:
                    await self.process_attack_damage(character, targets)
                elif character.weapon.attack_type == AttackType.RANGED:
                    await self.process_ranged_attack(character)
            if not character.alive and not character.body_removal_processed:
                character.body_removal_processed = True
                self._space.remove(
                    character.body, character.shape, character.hitbox_shape
                )
                for listener in self._listeners:
                    # make sure we tell remotes about the death, better to just send a health update
                    await self.publish(builders.build_character_updated(character))
                    listener.character_removed(character)
                if character in self.players:
                    logger.info("Player killed {}", character.uuid)
                    self._medical_manager.schedule_respawn(character)

    async def process_ranged_attack(self, character: Character):
        projectile = self._projectile_component.create_projectile(character)
        await self.publish(builders.build_projectile_created(character, projectile))
        character.should_process_attack = False

    async def process_attack_damage(
        self, attacker: Character, targets: list[Character]
    ):
        """Attack trigger frame reached, let's find who was hit and apply dmg"""
        attacker.should_process_attack = False
        for target in targets:
            if attacker.hitbox_shape.shapes_collide(target.shape).points:
                damage = 1
                target.handle_damage_received(damage)
                await self.publish(builders.build_character_damaged(target, damage))

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        for character in self._players + self._ai.enemies:
            if character.uuid == uuid:
                return character
        return None

    async def handle_message(self, msg: Message):
        await self._message_handler.handle_message(msg)

    async def publish(self, message: Message, **kwargs):
        await publish(bytes(message), **kwargs)

    def add_listener(self, listener: WorldListener):
        self._listeners.append(listener)

    @property
    def map(self) -> Map:
        return self._map

    @property
    def enemies(self) -> list[Enemy]:
        return self._ai.enemies

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def space(self) -> pymunk.Space:
        return self._space
