import logging
import os
from typing import Callable
from uuid import UUID

from pymunk import Vec2d

from nk_shared import builders
from nk_shared.proto import CharacterType, Message, PlayerJoinRequest

from nk.world import World
from nk.net.network import Network

TICKS_BEFORE_UPDATE = 6
logger = logging.getLogger(__name__)


class GameState:

    def __init__(
        self,
        network_initialized_callback: Callable | None = None,
        enemy_added_callback: Callable | None = None,
        character_attacked_callback: Callable | None = None,
    ):
        self.network_initialized_callback = network_initialized_callback
        self.enemy_added_callback = enemy_added_callback
        self.character_attacked_callback = character_attacked_callback
        self.network_ticks_til_update = TICKS_BEFORE_UPDATE
        self.world = World()
        self.network = Network()
        self.network.send(
            Message(
                player_join_request=PlayerJoinRequest(uuid=str(self.world.player.uuid))
            )
        )

    def update(self, dt: float):
        while self.network.has_messages():
            message = self.network.next()
            if message.player_join_response._serialized_on_wire:
                self.handle_player_join_response(message)
            elif message.character_updated._serialized_on_wire:
                self.handle_character_updated(message)
            elif message.character_attacked._serialized_on_wire:
                self.handle_character_attacked(message)
            elif message.character_damaged._serialized_on_wire:
                self.handle_character_damaged(message)
        self.handle_self_updated()

    def handle_self_updated(self):
        self.network_ticks_til_update -= 1
        if self.network_ticks_til_update <= 0:
            self.network_ticks_til_update = TICKS_BEFORE_UPDATE
            self.network.send(builders.build_character_updated(self.world.player))

    def handle_character_attacked(self, message: Message):
        details = message.character_attacked
        logger.info(details)
        if not details.uuid:
            logger.warn(f"character_attacked has no associated uuid!")
            return
        character = self.world.get_character_by_uuid(UUID(details.uuid))
        if character:
            character.attack()
            if self.character_attacked_callback:
                self.character_attacked_callback(character)
        else:
            logger.warn(
                f"character_attacked no character found with uuid {details.uuid}"
            )

    def handle_character_damaged(self, message: Message):
        details = message.character_damaged
        logger.info(details)
        if not details.uuid:
            logger.warn(f"character_damaged has no associated uuid!")
            return
        character = self.world.get_character_by_uuid(UUID(details.uuid))
        if character:
            character.handle_damage_received(details.damage)
        else:
            logger.warn(
                f"character_damaged no character found with uuid {details.uuid}"
            )

    def handle_character_updated(self, message: Message):
        details = message.character_updated
        uuid = UUID(details.uuid)
        character = self.world.get_enemy_by_uuid(uuid)
        if character:
            character.body.position = Vec2d(details.x, details.y)
            character.facing_direction = details.facing_direction
            character.moving_direction = details.moving_direction
        else:
            # TODO this might be a player? check character_type?
            character = self.world.add_enemy(
                uuid=uuid,
                start_x=details.x,
                start_y=details.y,
                character_type=CharacterType(details.character_type),
                facing_direction=details.facing_direction,
                moving_direction=details.moving_direction,
            )
            if self.enemy_added_callback:
                self.enemy_added_callback(character)

    def handle_player_join_response(self, message: Message):
        if not message.player_join_response.success:
            logger.info(f"Player join request failed, aborting")
            os._exit(1)
        x = message.player_join_response.x
        y = message.player_join_response.y
        self.world.player.body.position = (x, y)
        if self.network_initialized_callback:
            self.network_initialized_callback()
