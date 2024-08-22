"""Simulates the world's characters"""

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.map import Map
from nk_shared.models import AttackType, Character, Zone
from nk_shared.proto import Message

from app.ai import Ai
from app.messages.handler import MessageHandler
from app.models import Enemy, Player, WorldComponentProvider
from app.projectile_manager import ProjectileManager
from app.pubsub import publish
from app.settings import DATA_ROOT

HEAL_DST_SQ = 5
HEAL_AMT = 10.0
RESPAWN_TIME = 5.0


class World(WorldComponentProvider):  # pylint: disable=too-many-instance-attributes
    """Hold and simulate everything happening in the game."""

    def __init__(self, zone_name: str = "1"):
        self._space = pymunk.Space()
        self._zone = Zone.from_yaml_file(f"{DATA_ROOT}/zones/{zone_name}.yml")
        self._map = Map(self._zone.tmx_path, pygame=False)
        self._map.add_map_geometry_to_space(self._space)
        self._players: list[Player] = []
        self._ai_component = Ai(self, self._zone)
        self._projectile_component = ProjectileManager(self)
        self._message_component = MessageHandler(self)
        self._player_respawns: dict[str, float] = {}

    async def update(self, dt: float):
        await self._ai_component.update(dt)
        await self.update_characters(dt, self._players, self._ai_component.enemies)
        await self.update_characters(dt, self._ai_component.enemies, self._players)
        for player in self._players:
            self.update_medic(dt, player)
        await self.update_respawns(dt)
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
                if character.attack_type == AttackType.MELEE:
                    await self.process_attack_damage(character, targets)
                elif character.attack_type == AttackType.RANGED:
                    await self.process_ranged_attack(character)
            if not character.alive and not character.body_removal_processed:
                character.body_removal_processed = True
                self._space.remove(
                    character.body, character.shape, character.hitbox_shape
                )
                if character in self.players:
                    logger.info("Player killed {}", character.uuid)
                    self._player_respawns[character.uuid] = RESPAWN_TIME

    async def update_respawns(self, dt: float):
        """Update respawn timers for players"""
        for player_uuid in list(self._player_respawns):
            respawn_time = self._player_respawns[player_uuid]
            respawn_time -= dt
            if respawn_time <= 0:
                del self._player_respawns[player_uuid]
                player = self.get_character_by_uuid(player_uuid)
                await self.respawn_player(player)
            else:
                self._player_respawns[player_uuid] = respawn_time

    async def respawn_player(self, player: Player):
        player.hp = player.hp_max

        closest_dst_sq = float("inf")
        spawn_point = None
        for medic in self._zone.medics:
            dst_sq = player.position.get_dist_sqrd((medic.x, medic.y))
            if dst_sq < closest_dst_sq:
                closest_dst_sq = dst_sq
                spawn_point = (medic.x, medic.y)
        player.body.position = spawn_point
        await self.publish(builders.build_player_respawned(player))

    def update_medic(self, dt: float, player: Player):
        """Check if player is in range of a medic and heal if so"""
        for medic in self._zone.medics:
            dst_sq = player.position.get_dist_sqrd((medic.x, medic.y))
            if dst_sq < HEAL_DST_SQ:
                player.handle_healing_received(HEAL_AMT * dt)
                return

    async def process_ranged_attack(self, character: Character):
        projectile = self._projectile_component.create_projectile(character)
        await self.publish(builders.build_projectile_created(projectile))
        character.should_process_attack = False
        logger.debug("Projectile created: {}", projectile.uuid)

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
        for character in self._players + self._ai_component.enemies:
            if character.uuid == uuid:
                return character
        return None

    async def handle_message(self, msg: Message):
        await self._message_component.handle_message(msg)

    async def publish(self, message: Message, **kwargs) -> None:
        await publish(bytes(message), **kwargs)

    @property
    def map(self) -> Map:
        return self._map

    @property
    def enemies(self) -> list[Enemy]:
        return self._ai_component.enemies

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def space(self) -> pymunk.Space:
        return self._space
