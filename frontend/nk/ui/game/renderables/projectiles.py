from functools import lru_cache
from typing import Iterable

import pygame
from nk_shared.models import Projectile

from nk.game.world import World
from nk.settings import NK_DATA_ROOT
from nk.ui.game.models import UIInterface
from nk.ui.game.renderables.models import (
    BlittableRenderable,
    Renderable,
    TracerRenderable,
)
from nk.ui.game.renderables.util import renderables_generate_key

PROJECTILE_LENGTH_SCALAR = 50
one_one_surface = pygame.Surface((1, 1))


def generate_projectile_renderables(
    world: World, ui_interface: UIInterface
) -> Iterable[Renderable]:
    for projectile in world.projectile_manager.projectiles:
        if projectile.weapon.projectile_image_path == "tracer":
            method = generate_projectile_tracer_renderable
        else:
            method = generate_projectile_blittable_renderable
        yield method(world, ui_interface, projectile)


def generate_projectile_blittable_renderable(
    world: World, ui_interface: UIInterface, projectile: Projectile
) -> BlittableRenderable:
    image = load_projectile_image(projectile.weapon.projectile_image_path)
    blit_x, blit_y = ui_interface.calculate_draw_coordinates(
        projectile.x, projectile.y, image
    )
    bottom_y = blit_y + image.get_height()
    key = renderables_generate_key(0, bottom_y)
    return BlittableRenderable(key, image, (blit_x, blit_y))


def generate_projectile_tracer_renderable(
    world: World, ui_interface: UIInterface, projectile: Projectile
) -> TracerRenderable:
    start = ui_interface.calculate_draw_coordinates(
        projectile.x, projectile.y, one_one_surface
    )
    end = ui_interface.calculate_draw_coordinates(
        projectile.x + projectile.dx / PROJECTILE_LENGTH_SCALAR,
        projectile.y + projectile.dy / PROJECTILE_LENGTH_SCALAR,
        one_one_surface,
    )
    bottom_y = max(start[1], end[1])
    key = renderables_generate_key(0, bottom_y)
    return TracerRenderable(key, start, end)


@lru_cache
def load_projectile_image(image_path: str):
    path = f"{NK_DATA_ROOT}/projectiles/{image_path}.png"
    return pygame.image.load(path).convert_alpha()
