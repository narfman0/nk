# projectile_manager.py
from functools import lru_cache

import pygame
from nk.settings import NK_DATA_ROOT
from nk.ui.models import GameUICalculator
from nk.ui.renderables import BlittableRenderable, renderables_generate_key
from nk.world import World


def generate_projectile_renderables(world: World, calculator: GameUICalculator):
    for projectile in world.projectiles:
        image = load_projectile_image(projectile.attack_profile.image_path)
        blit_x, blit_y = calculator.calculate_draw_coordinates(
            projectile.x, projectile.y, image
        )
        bottom_y = blit_y - calculator.cam_y + image.get_height()
        yield BlittableRenderable(
            renderables_generate_key(world.map.get_1f_layer_id(), bottom_y),
            image,
            (blit_x - calculator.cam_x, blit_y - calculator.cam_y),
        )


@lru_cache
def load_projectile_image(image_path: str):
    path = f"{NK_DATA_ROOT}/projectiles/{image_path}.png"
    return pygame.image.load(path).convert_alpha()
