import pygame
import pygame_gui
from nk_shared.models.character import Character

from nk.settings import HEIGHT, NK_DATA_ROOT, WIDTH


class GameGui:
    def __init__(self):
        self.font = pygame.font.Font(f"{NK_DATA_ROOT}/fonts/HarmonicFont.ttf", 24)
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.white = pygame.Color("white")
        self.dt_ewma = 0

    def draw(  # pylint: disable=too-many-arguments
        self,
        player: Character,
        surface: pygame.Surface,
        renderable_count: int,
        character_count: int,
        mouse_pos: tuple[float, float],
        terminal_text: str,
    ):
        x, y = player.position
        self.manager.draw_ui(surface)
        guiables = [
            f"dt: {int(self.dt_ewma*1000)}ms",
            f"renderables: {renderable_count}",
            f"HP: {player.hp}",
            f"Ammo: {player.rounds_remaining}",
            f"x,y: {int(x)},{int(y)}",
            f"Characters: {character_count}",
            f"Mouse: {int(mouse_pos[0])},{int(mouse_pos[1])}",
        ]
        draw_y = 0
        for guiable in guiables:
            text_sf = self.font.render(guiable, False, self.white)
            surface.blit(text_sf, (32, draw_y))
            draw_y += 32
        if terminal_text is not None:
            terminal_sf = self.font.render(terminal_text, False, self.white)
            pygame.draw.rect(
                surface,
                pygame.Color(0, 0, 0, 128),
                (
                    32 - 4,
                    HEIGHT - 32 - 4,
                    terminal_sf.width + 8,
                    terminal_sf.height + 8,
                ),
            )
            surface.blit(terminal_sf, (32, HEIGHT - 32))

    def update(self, dt: float):
        self.manager.update(dt)
        self.dt_ewma = 0.95 * self.dt_ewma + 0.05 * dt
