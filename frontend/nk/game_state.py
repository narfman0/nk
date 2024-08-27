from typing import Callable

from betterproto import serialized_on_wire
from nk_shared import builders
from nk_shared.proto import Message

from nk.game.world import World
from nk.net.messages.character_message_handler import CharacterMessageHandler
from nk.net.messages.player_message_handler import PlayerMessageHandler
from nk.net.messages.projectile_message_handler import ProjectileMessageHandler
from nk.net.network import Network

TICKS_BEFORE_UPDATE = 6


class GameState:

    def __init__(self):
        self.character_msg_handler: CharacterMessageHandler = None
        self.player_msg_handler: PlayerMessageHandler = None
        self.projectile_msg_handler: ProjectileMessageHandler = None
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
                    self.player_msg_handler.handle_player_respawned(message)
                elif serialized_on_wire(message.projectile_created):
                    self.projectile_msg_handler.handle_projectile_created(message)
                elif serialized_on_wire(message.projectile_destroyed):
                    self.projectile_msg_handler.handle_projectile_destroyed(message)
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

    def handle_player_join_response(self, message: Message):
        details = message.player_join_response
        self.world = World(details.uuid, details.x, details.y)
        self.character_msg_handler = CharacterMessageHandler(self.world)
        self.player_msg_handler = PlayerMessageHandler(self.world)
        self.projectile_msg_handler = ProjectileMessageHandler(self.world)
        if self.player_joined_callback:
            self.player_joined_callback()  # pylint: disable=not-callable
