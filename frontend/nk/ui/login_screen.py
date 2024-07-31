from pygame import Event

from nk.game_state import GameState
from nk.ui.load_screen import LoadScreen
from nk.ui.screen import Screen, ScreenManager


class LoginScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = GameState()

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        # self.game_state.update()

        self.screen_manager.pop()
        self.screen_manager.push(LoadScreen(self.screen_manager, self.game_state))
