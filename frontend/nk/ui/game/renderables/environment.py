from nk_shared.map import Tilemap
from nk_shared.models.zone import Environment

from nk.ui.game.models import UIInterface
from nk.ui.game.renderables.map import generate_map_renderables


def generate_environment_renderables(
    ui_interface: UIInterface, environment_features: list[Environment]
):
    for environment in environment_features:
        tilemap = Tilemap(environment.tmx_name)
        yield from generate_map_renderables(
            ui_interface=ui_interface,
            ground=False,
            tilemap=tilemap,
            tile_offset_y=environment.center_y - tilemap.height // 2,
            tile_offset_x=environment.center_x - tilemap.width // 2,
        )
