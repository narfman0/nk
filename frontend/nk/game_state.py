import logging
import os
from typing import Callable

from betterproto import serialized_on_wire
from pymunk import Vec2d

from nk_shared import builders
from nk_shared.proto import (
    CharacterType,
    Direction,
    Message,
    PlayerJoinRequest,
    PlayerLoginRequest,
)

from nk.world import World
from nk.net.network import Network

TICKS_BEFORE_UPDATE = 6
logger = logging.getLogger(__name__)


class GameState:

    def __init__(self):
        self.network_initialized_callback: Callable = None
        self.login_callback: Callable = None
        self.character_added_callback: Callable = None
        self.character_attacked_callback: Callable = None
        self.network_ticks_til_update = TICKS_BEFORE_UPDATE
        self.world = World()
        self.network = Network()

    def update(self):
        while self.network.has_messages():
            message = self.network.next()
            if serialized_on_wire(message.player_join_response):
                self.handle_player_join_response(message)
            elif serialized_on_wire(message.player_login_response):
                self.handle_player_login_response(message)
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
        self.handle_self_updated()

    def login(self, email: str, password: str, callback: Callable):
        self.login_callback = callback
        self.network.connect(email, password)
        details = PlayerLoginRequest(email=email, password=password)
        self.network.send(Message(player_login_request=details))

    def join_request(self, callback: Callable):
        self.network_initialized_callback = callback
        self.network.send(
            Message(
                player_join_request=PlayerJoinRequest(uuid=str(self.world.player.uuid))
            )
        )

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
            character.attack()
            if self.character_attacked_callback:
                # pylint: disable-next=not-callable
                self.character_attacked_callback(character)
        else:
            logger.warning(
                "character_attacked no character found with uuid %s", details.uuid
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
        else:
            logger.warning(
                "character_damaged no character found with uuid %s", details.uuid
            )

    def handle_character_updated(self, message: Message):
        details = message.character_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.body.position = Vec2d(details.x, details.y)
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

    def handle_player_login_response(self, message: Message):
        if not message.player_login_response.success:
            logger.info("Player login request failed, aborting")
            os._exit(1)
        if self.login_callback:
            self.login_callback()  # pylint: disable=not-callable

    def handle_player_join_response(self, message: Message):
        if not message.player_join_response.success:
            logger.info("Player join request failed, aborting")
            os._exit(1)
        x = message.player_join_response.x
        y = message.player_join_response.y
        self.world.player.body.position = (x, y)
        if self.network_initialized_callback:
            self.network_initialized_callback()  # pylint: disable=not-callable

    def handle_projectile_created(self, message: Message):
        self.world.create_projectile(message.projectile_created.projectile)

    def handle_projectile_destroyed(self, message: Message):
        details = message.projectile_destroyed
        projectile = self.world.get_projectile_by_uuid(details.uuid)
        if projectile:
            self.world.projectiles.remove(projectile)
