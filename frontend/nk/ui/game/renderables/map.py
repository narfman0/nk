from nk_shared.map import Map

from nk.ui.game.models import UIInterface
from nk.ui.game.renderables.models import BlittableRenderable
from nk.ui.game.renderables.util import renderables_generate_key


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
