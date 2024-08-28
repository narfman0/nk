# pylint: disable=no-member
import pygame

from nk.settings import FPS, HEIGHT, WIDTH
from nk.ui.login_screen import LoginScreen
from nk.ui.screen import ScreenManager
from nk_shared.profiling import begin_profiling, end_profiling


def main():  # pylint: disable=too-many-locals
    pygame.init()
    pygame.display.set_caption("nk")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    clock = pygame.time.Clock()

    screen_manager = ScreenManager()
    screen_manager.push(LoginScreen(screen_manager))

    begin_profiling()
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            else:
                events.append(event)
        # current screen can change in update, so let's save current_screen
        current_screen = screen_manager.current
        current_screen.update(dt, events)
        surface.fill((0, 0, 0))
        current_screen.draw(surface)
        pygame.display.update()
    end_profiling()
    pygame.quit()


if __name__ == "__main__":
    main()
