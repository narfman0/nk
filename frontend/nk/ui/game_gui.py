import pygame
import pygame_gui
from nk_shared.models.character import Character

from nk.settings import HEIGHT, WIDTH


class GameGui:
    def __init__(self):
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        width_height = (256, 50)
        left = 100
        self._hp_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((left, 64), width_height),
            text="",
            manager=self.manager,
        )
        self._debug_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((left, 96), width_height),
            text="",
            manager=self.manager,
        )

    def draw(self, player: Character, surface: pygame.Surface):
        self._hp_label.set_text(f"HP: {player.hp}")
        x, y = player.position
        self._debug_label.set_text(f"x,y: {int(x)},{int(y)}")
        self.manager.draw_ui(surface)

    def update(self, dt: float):
        self.manager.update(dt)
