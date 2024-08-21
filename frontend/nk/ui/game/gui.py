import pygame
import pygame_gui
from nk_shared.models.character import Character

from nk.settings import HEIGHT, NK_DATA_ROOT, WIDTH


class GameGui:
    def __init__(self):
        self.font = pygame.font.Font(f"{NK_DATA_ROOT}/fonts/HarmonicFont.ttf", 24)
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.dt_ewma = 0

    def draw(self, player: Character, surface: pygame.Surface):
        x, y = player.position
        self.manager.draw_ui(surface)

        text_sf = self.font.render(
            f"dt: {int(self.dt_ewma*1000)}ms", False, pygame.Color("white")
        )
        surface.blit(text_sf, (32, 0))
        text_sf = self.font.render(f"HP: {player.hp}", False, pygame.Color("white"))
        surface.blit(text_sf, (32, 32))
        text_sf = self.font.render(
            f"x,y: {int(x)},{int(y)}", False, pygame.Color("white")
        )
        surface.blit(text_sf, (32, 64))

    def update(self, dt: float):
        self.manager.update(dt)
        self.dt_ewma = 0.95 * self.dt_ewma + 0.05 * dt
