import logging
from pygame.event import Event
import os

from nk.game.world import World
from nk.ui.screen import Screen, ScreenManager
from nk.ui.game_screen import GameScreen
from nk.net.network import Network
from nk_shared.proto import Message, PlayerJoinRequest

logger = logging.getLogger(__name__)


class LoadScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.world = World()
        self.network = Network()
        self.network.send(
            Message(
                player_join_request=PlayerJoinRequest(uuid=str(self.world.player.uuid))
            )
        )

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        while self.network.has_messages():
            message = self.network.next()
            if message.player_join_response._serialized_on_wire:
                if not message.player_join_response.success:
                    logger.info(f"Player join request failed, aborting")
                    os._exit(1)
                x = message.player_join_response.x
                y = message.player_join_response.y
                self.world.player.body.position = (x, y)
                self.screen_manager.pop()
                self.screen_manager.push(
                    GameScreen(self.screen_manager, self.world, self.network)
                )
