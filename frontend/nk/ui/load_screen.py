from pygame.event import Event
from nk.game.world import World
from nk.ui.screen import Screen, ScreenManager
from nk.ui.game_screen import GameScreen


class LoadScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        self.screen_manager.pop()
        self.screen_manager.push(GameScreen(self.screen_manager, World()))
