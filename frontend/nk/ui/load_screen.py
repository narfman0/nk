from loguru import logger
from pygame.event import Event

from nk.game_state import GameState
from nk.ui.game_screen import GameScreen
from nk.ui.screen import Screen, ScreenManager


class LoadScreen(Screen):

    def __init__(  # pylint: disable=too-many-arguments
        self,
        screen_manager: ScreenManager,
        game_state: GameState,
        email: str,
        password: str,
        register: bool,
    ):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = game_state
        if register:
            self.game_state.register(email, password)
        self.game_state.login(email, password, self.handle_player_joined)
        logger.info("Logging in to %s", email)

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        self.game_state.update()

    def handle_player_joined(self):
        logger.info("Player joined, loading...")
        self.screen_manager.pop()
        self.screen_manager.push(GameScreen(self.screen_manager, self.game_state))
