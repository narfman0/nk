import logging
from pstats import SortKey
import pygame

from nk_shared.util.logging import initialize_logging

from nk.settings import *
from nk.ui.screen import ScreenManager
from nk.ui.load_screen import LoadScreen

LOGGER = logging.getLogger(__name__)


def main():
    initialize_logging()
    pygame.init()
    pygame.display.set_caption("nk")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    clock = pygame.time.Clock()

    screen_manager = ScreenManager()
    screen_manager.push(LoadScreen(screen_manager))

    if ENABLE_PROFILING:
        import cProfile, pstats, io

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
        with open("pstats.log", "w+") as f:
            f.write(s.getvalue())
    pygame.quit()


if __name__ == "__main__":
    main()
