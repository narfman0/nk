import logging
from pygame.event import Event

from nk.game_state import GameState
from nk.ui.screen import Screen, ScreenManager
from nk.ui.game_screen import GameScreen

logger = logging.getLogger(__name__)


class LoadScreen(Screen):
    def __init__(
        self,
        screen_manager: ScreenManager,
        game_state: GameState,
        username: str,
        password: str,
    ):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = game_state
        self.game_state.login(username, password, self.handle_login_success)
        logger.info("Logging in to %s", username)

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        self.game_state.update()

    def handle_login_success(self):
        logger.info("Login success!")
        self.game_state.join_request(self.handle_network_initialized)

    def handle_network_initialized(self):
        logger.info("Network initialized, loading...")
        self.screen_manager.pop()
        self.screen_manager.push(GameScreen(self.screen_manager, self.game_state))
