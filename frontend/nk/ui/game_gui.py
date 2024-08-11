import pygame
import pygame_gui
from nk_shared.models.character import Character

from nk.settings import HEIGHT, NK_DATA_ROOT, WIDTH


class GameGui:
    def __init__(self):
        self.font = pygame.font.Font(f"{NK_DATA_ROOT}/fonts/HarmonicFont.ttf", 24)
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        width_height = (256, 50)
        left = 32
        self._hp_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((left, 32), width_height),
            text="",
            manager=self.manager,
        )
        self._debug_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((left, 64), width_height),
            text="",
            manager=self.manager,
        )

    def draw(self, player: Character, surface: pygame.Surface):
        x, y = player.position
        # self._hp_label.set_text(f"HP: {player.hp}")
        # self._debug_label.set_text(f"x,y: {int(x)},{int(y)}")
        self.manager.draw_ui(surface)

        text_sf = self.font.render(f"HP: {player.hp}", False, pygame.Color("white"))
        surface.blit(text_sf, (32, 32))
        text_sf = self.font.render(
            f"x,y: {int(x)},{int(y)}", False, pygame.Color("white")
        )
        surface.blit(text_sf, (32, 64))

    def update(self, dt: float):
        self.manager.update(dt)
