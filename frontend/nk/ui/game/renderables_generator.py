from functools import lru_cache

import pygame
from nk_shared.map import Map
from nk_shared.models.zone import Environment

from nk.game.world import World
from nk.settings import NK_DATA_ROOT
from nk.ui.game.models import UIInterface
from nk.ui.game.renderables import BlittableRenderable, renderables_generate_key


def generate_projectile_renderables(world: World, ui_interface: UIInterface):
    for projectile in world.projectile_manager.projectiles:
        image = load_projectile_image(projectile.weapon.projectile_image_path)
        blit_x, blit_y = ui_interface.calculate_draw_coordinates(
            projectile.x, projectile.y, image
        )
        bottom_y = blit_y + image.get_height()
        yield BlittableRenderable(
            renderables_generate_key(world.map.get_1f_layer_id(), bottom_y),
            image,
            (blit_x, blit_y),
        )


def generate_map_renderables(  # pylint: disable=too-many-locals
    ui_interface: UIInterface,
    ground: bool,
    tilemap: Map,
    tile_offset_x: int = 0,
    tile_offset_y: int = 0,
):
    """We can statically generate the blit coords once in the beginning,
    avoiding a bunch of coordinate conversions."""
    ground_ids = tilemap.get_ground_layer_ids()
    for layer in range(tilemap.get_tile_layer_count()):
        if layer not in ground_ids if ground else layer in ground_ids:
            continue
        x_offset, y_offset = tilemap.get_layer_offsets(layer)
        for x in range(0, tilemap.width):
            for y in range(0, tilemap.height):
                blit_image = tilemap.get_tile_image(x, y, layer)
                if blit_image:
                    blit_x, blit_y = ui_interface.calculate_draw_coordinates(
                        x + tile_offset_x, y + tile_offset_y, blit_image
                    )
                    blit_coords = (blit_x + x_offset, blit_y + y_offset)
                    img_height = blit_image.get_height()
                    bottom_y = blit_y + y_offset + img_height - 8
                    yield BlittableRenderable(
                        renderables_generate_key(layer, bottom_y),
                        blit_image,
                        blit_coords,
                    )


def generate_environment_renderables(
    ui_interface: UIInterface, environment_features: list[Environment]
):
    for environment in environment_features:
        tilemap = Map(environment.tmx_name)
        yield from generate_map_renderables(
            ui_interface=ui_interface,
            ground=False,
            tilemap=tilemap,
            tile_offset_y=environment.center_y - tilemap.height // 2,
            tile_offset_x=environment.center_x - tilemap.width // 2,
        )


@lru_cache
def load_projectile_image(image_path: str):
    path = f"{NK_DATA_ROOT}/projectiles/{image_path}.png"
    return pygame.image.load(path).convert_alpha()
