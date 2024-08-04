# pylint: disable=no-member
from pstats import SortKey

import pygame

from nk.settings import ENABLE_PROFILING, FPS, HEIGHT, WIDTH
from nk.ui.login_screen import LoginScreen
from nk.ui.screen import ScreenManager


def main():  # pylint: disable=too-many-locals
    pygame.init()
    pygame.display.set_caption("nk")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    clock = pygame.time.Clock()

    screen_manager = ScreenManager()
    screen_manager.push(LoginScreen(screen_manager))

    if ENABLE_PROFILING:
        import cProfile  # pylint: disable=import-outside-toplevel
        import io  # pylint: disable=import-outside-toplevel
        import pstats  # pylint: disable=import-outside-toplevel

        pr = cProfile.Profile()
        pr.enable()
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

    if ENABLE_PROFILING:
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open("pstats.log", "w+") as f:  # pylint: disable=unspecified-encoding
            f.write(s.getvalue())
    pygame.quit()


if __name__ == "__main__":
    main()
