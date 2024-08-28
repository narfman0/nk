import pygame
import pygame_gui
from nk_shared.models.character import Character

from nk.settings import HEIGHT, NK_DATA_ROOT, WIDTH


class GameGui:
    def __init__(self):
        self.font = pygame.font.Font(f"{NK_DATA_ROOT}/fonts/HarmonicFont.ttf", 24)
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.dt_ewma = 0

    def draw(
        self,
        player: Character,
        surface: pygame.Surface,
        renderable_count: int,
        draw_ticks: int,
        player_count: int,
        enemy_count: int,
    ):
        x, y = player.position
        self.manager.draw_ui(surface)
        guiables = [
            f"dt: {int(self.dt_ewma*1000)}ms",
            f"ticks: {draw_ticks}",
            f"renderables: {renderable_count}",
            f"HP: {player.hp}",
            f"Ammo: {player.rounds_remaining}",
            f"x,y: {int(x)},{int(y)}",
            f"Players: {player_count}",
            f"Enemies: {enemy_count}",
        ]
        draw_y = 0
        for guiable in guiables:
            text_sf = self.font.render(guiable, False, pygame.Color("white"))
            surface.blit(text_sf, (32, draw_y))
            draw_y += 32

    def update(self, dt: float):
        self.manager.update(dt)
        self.dt_ewma = 0.95 * self.dt_ewma + 0.05 * dt
