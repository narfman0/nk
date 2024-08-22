from collections import deque
from typing import Callable

from betterproto import serialized_on_wire
from loguru import logger
from nk_shared import builders
from nk_shared.proto import CharacterType, Direction, Message
from pymunk import Vec2d

from nk.net.network import Network
from nk.world import World

TICKS_BEFORE_UPDATE = 6


class GameState:

    def __init__(self):
        self.player_joined_callback: Callable = None
        self.character_added_callback: Callable = None
        self.character_attacked_callback: Callable = None
        self.network_ticks_til_update = TICKS_BEFORE_UPDATE
        self.world: World = None
        self.network = Network()

    def update(self, _dt: float):
        while self.network.has_messages():
            message = self.network.next()
            if self.world:
                if serialized_on_wire(message.character_position_updated):
                    self.handle_character_position_updated(message)
                if serialized_on_wire(message.character_direction_updated):
                    self.handle_character_direction_updated(message)
                elif serialized_on_wire(message.character_updated):
                    self.handle_character_updated(message)
                elif serialized_on_wire(message.character_attacked):
                    self.handle_character_attacked(message)
                elif serialized_on_wire(message.character_damaged):
                    self.handle_character_damaged(message)
                elif serialized_on_wire(message.projectile_created):
                    self.handle_projectile_created(message)
                elif serialized_on_wire(message.projectile_destroyed):
                    self.handle_projectile_destroyed(message)
            else:
                if serialized_on_wire(message.player_join_response):
                    self.handle_player_join_response(message)
        if self.world:
            self.handle_self_updated()

    def login(self, email: str, password: str, callback: Callable):
        access_token = self.network.login(email, password)
        self.network.connect(access_token)
        self.player_joined_callback = callback

    def register(self, email: str, password: str):
        self.network.register(email, password)

    def handle_self_updated(self):
        self.network_ticks_til_update -= 1
        if self.network_ticks_til_update <= 0:
            self.network_ticks_til_update = TICKS_BEFORE_UPDATE
            self.network.send(builders.build_character_updated(self.world.player))

    def handle_character_attacked(self, message: Message):
        details = message.character_attacked
        logger.info(details)
        if not details.uuid:
            logger.warning("character_attacked has no associated uuid!")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.attack(details.direction)
            if self.character_attacked_callback:
                # pylint: disable-next=not-callable
                self.character_attacked_callback(character)
        else:
            logger.warning(
                "character_attacked no character found with uuid {}", details.uuid
            )

    def handle_character_damaged(self, message: Message):
        details = message.character_damaged
        logger.info(details)
        if not details.uuid:
            logger.warning("character_damaged has no associated uuid!")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.handle_damage_received(details.damage)
            character.hp = details.hp
        else:
            logger.warning(
                "character_damaged no character found with uuid {}", details.uuid
            )

    def handle_character_direction_updated(self, message: Message):
        details = message.character_direction_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.facing_direction = Direction(details.facing_direction)
            character.moving_direction = Direction(details.moving_direction)
        else:
            logger.warning("No character found with uuid: {}", details.uuid)

    def handle_character_position_updated(self, message: Message):
        details = message.character_position_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.body.position = Vec2d(details.x, details.y)
            character.body.velocity = Vec2d(details.dx, details.dy)
        else:
            logger.warning("No character found with uuid: {}", details.uuid)

    def handle_character_updated(self, message: Message):
        details = message.character_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.body.position = Vec2d(details.x, details.y)
            character.body.velocity = Vec2d(details.dx, details.dy)
        else:
            if details.character_type == CharacterType.CHARACTER_TYPE_PIGSASSIN:
                character = self.world.add_player(
                    uuid=details.uuid,
                    start_x=details.x,
                    start_y=details.y,
                )
            else:
                character = self.world.add_enemy(
                    uuid=details.uuid,
                    start_x=details.x,
                    start_y=details.y,
                    character_type=CharacterType(details.character_type),
                )
            if self.character_added_callback:
                self.character_added_callback(character)  # pylint: disable=not-callable
        character.facing_direction = Direction(details.facing_direction)
        character.moving_direction = Direction(details.moving_direction)
        character.hp = details.hp

    def handle_player_join_response(self, message: Message):
        details = message.player_join_response
        self.world = World(details.uuid, details.x, details.y)
        if self.player_joined_callback:
            self.player_joined_callback()  # pylint: disable=not-callable

    def handle_projectile_created(self, message: Message):
        self.world.create_projectile(message.projectile_created.projectile)

    def handle_projectile_destroyed(self, message: Message):
        details = message.projectile_destroyed
        projectile = self.world.get_projectile_by_uuid(details.uuid)
        if projectile:
            self.world.projectiles.remove(projectile)
