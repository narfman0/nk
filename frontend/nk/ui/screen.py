from pygame.event import Event
from pygame.surface import Surface


class Screen:
    def __init__(self):
        self.init()

    def init(self):
        pass

    def update(self, dt: float, events: list[Event]):
        pass

    def draw(self, surface: Surface):
        pass

    def kill(self):
        pass

    def reinit(self):
        self.kill()
        self.init()


class ScreenManager:
    def __init__(self):
        self.screens: list[Screen] = []

    def push(self, screen: Screen):
        if self.current:
            self.current.kill()
        self.screens.append(screen)

    def pop(self):
        if self.current:
            self.current.kill()
        self.screens.pop()
        if self.current:
            self.current.init()

    @property
    def current(self) -> Screen:
        if self.screens:
            return self.screens[-1]
        return None
