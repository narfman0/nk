import logging
import os

from pygame.event import Event

from nk.game_state import GameState
from nk.net import Network
from nk.ui.screen import Screen, ScreenManager
from nk.ui.game_screen import GameScreen
from nk.world import World

logger = logging.getLogger(__name__)


class LoadScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager
        self.game_state = GameState(
            network_initialized_callback=self.network_initialized
        )

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        self.game_state.update(dt)

    def network_initialized(self):
        self.screen_manager.pop()
        self.screen_manager.push(GameScreen(self.screen_manager, self.game_state))
