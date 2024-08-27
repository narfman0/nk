from typing import Callable

from nk_shared import builders
from nk_shared.proto import Message

from nk.game.world import World
from nk.net.messages.character_message_handler import CharacterMessageHandler
from nk.net.messages.message_handler import MessageHandler
from nk.net.messages.player_join_response_handler import PlayerJoinResponseHandler
from nk.net.messages.player_message_handler import PlayerMessageHandler
from nk.net.messages.projectile_message_handler import ProjectileMessageHandler
from nk.net.network import Network

TICKS_BEFORE_UPDATE = 6


class GameState:

    def __init__(self):
        self.character_msg_handler: CharacterMessageHandler = None
        self.message_handlers: list[MessageHandler] = []
        self.message_handlers.append(
            PlayerJoinResponseHandler(self.handle_player_join_response)
        )
        self.player_joined_callback: Callable = None
        self.network_ticks_til_update = TICKS_BEFORE_UPDATE
        self.world: World = None
        self.network = Network()

    def update(self, _dt: float):
        while self.network.has_messages():
            message = self.network.next()
            self.handle_network_message(message)
        if self.world:
            self.send_self_updated()

    def handle_network_message(self, message: Message):
        for handler in list(self.message_handlers):
            if handler.handle_message(message):
                return

    def login(self, email: str, password: str, callback: Callable):
        access_token = self.network.login(email, password)
        self.network.connect(access_token)
        self.player_joined_callback = callback

    def register(self, email: str, password: str):
        self.network.register(email, password)

    def send_self_updated(self):
        self.network_ticks_til_update -= 1
        if self.network_ticks_til_update <= 0:
            self.network_ticks_til_update = TICKS_BEFORE_UPDATE
            self.network.send(builders.build_character_updated(self.world.player))

    def handle_player_join_response(self, message: Message):
        details = message.player_join_response
        self.world = World(details.uuid, details.x, details.y)
        self.character_msg_handler = CharacterMessageHandler(self.world)
        self.message_handlers.clear()  # remove PlayerJoinResponseHandler
        self.message_handlers.append(self.character_msg_handler)
        self.message_handlers.append(PlayerMessageHandler(self.world))
        self.message_handlers.append(ProjectileMessageHandler(self.world))
        if self.player_joined_callback:
            self.player_joined_callback()  # pylint: disable=not-callable
