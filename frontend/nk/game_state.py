from typing import Callable

from betterproto import serialized_on_wire
from loguru import logger
from nk_shared import builders
from nk_shared.proto import Message
from pymunk import Vec2d

from nk.game.world import World
from nk.net.character_message_handler import CharacterMessageHandler
from nk.net.network import Network

TICKS_BEFORE_UPDATE = 6


class GameState:

    def __init__(self):
        self.character_msg_handler: CharacterMessageHandler = None
        self.player_joined_callback: Callable = None
        self.network_ticks_til_update = TICKS_BEFORE_UPDATE
        self.world: World = None
        self.network = Network()

    def update(self, _dt: float):  # pylint: disable=too-many-branches
        while self.network.has_messages():
            message = self.network.next()
            if self.world:
                if serialized_on_wire(message.character_position_updated):
                    self.character_msg_handler.handle_character_position_updated(
                        message
                    )
                if serialized_on_wire(message.character_direction_updated):
                    self.character_msg_handler.handle_character_direction_updated(
                        message
                    )
                elif serialized_on_wire(message.character_updated):
                    self.character_msg_handler.handle_character_updated(message)
                elif serialized_on_wire(message.character_attacked):
                    self.character_msg_handler.handle_character_attacked(message)
                elif serialized_on_wire(message.character_damaged):
                    self.character_msg_handler.handle_character_damaged(message)
                elif serialized_on_wire(message.character_reloaded):
                    self.character_msg_handler.handle_character_reloaded(message)
                elif serialized_on_wire(message.player_respawned):
                    self.handle_player_respawned(message)
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

    def handle_player_respawned(self, message: Message):
        details = message.player_respawned
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.hp = character.hp_max
            character.body.position = Vec2d(details.x, details.y)
        else:
            logger.warning(
                "character_damaged no character found with uuid {}", details.uuid
            )

    def handle_player_join_response(self, message: Message):
        details = message.player_join_response
        self.world = World(details.uuid, details.x, details.y)
        self.character_msg_handler = CharacterMessageHandler(self.world)
        if self.player_joined_callback:
            self.player_joined_callback()  # pylint: disable=not-callable

    def handle_projectile_created(self, message: Message):
        if message.projectile_created.origin_uuid == self.world.player.uuid:
            return
        self.world.projectile_manager.create_projectile(message.projectile_created)

    def handle_projectile_destroyed(self, message: Message):
        details = message.projectile_destroyed
        projectile = self.world.projectile_manager.get_projectile_by_uuid(details.uuid)
        if projectile:
            self.world.projectile_manager.projectiles.remove(projectile)
