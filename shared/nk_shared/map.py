from functools import lru_cache

from loguru import logger
import pymunk
import pytmx

from nk_shared.settings import DATA_ROOT


class Map:
    def __init__(self, area: str, headless=False):
        self.area = area
        path = f"{DATA_ROOT}/tiled/tmx/{area}.tmx"
        if headless:
            self._tmxdata = pytmx.TiledMap(path)
        else:
            self._tmxdata = pytmx.load_pygame(path)

    def get_start_tile(self) -> tuple[int, int]:
        x, y = map(int, self._tmxdata.properties.get("StartXY").split(","))
        return (x, y)

    @lru_cache(maxsize=2048)
    def get_tile_image(self, tile_x: int, tile_y: int, layer: int):
        return self._tmxdata.get_tile_image(tile_x, tile_y, layer)

    def get_tile_layer_count(self):
        return len(list(self._tmxdata.visible_tile_layers))

    def add_map_geometry_to_space(
        self, space: pymunk.Space, tile_offset_x: int = 0, tile_offset_y: int = 0
    ):
        for layer in range(self.get_tile_layer_count()):
            impassable = self.get_layer_name(layer) == "impassable"
            for y in range(self.height):
                for x in range(self.width):
                    gid = self._tmxdata.get_tile_gid(x, y, layer)
                    tile_props = self._tmxdata.get_tile_properties_by_gid(gid) or {}
                    colliders: list = tile_props.get("colliders", [])
                    impassable_tile = impassable and gid
                    if colliders or impassable_tile:
                        body = pymunk.Body(body_type=pymunk.Body.STATIC)
                        body.position = (
                            0.5 + x + tile_offset_x,
                            0.5 + y + tile_offset_y,
                        )
                        poly = pymunk.Poly.create_box(body, size=(1, 1))
                        poly.mass = 10
                        space.add(body, poly)
        return False

    @lru_cache(maxsize=32)
    def get_layer_name(self, layer: int) -> str:
        return self._tmxdata.layers[layer].name

    @lru_cache(maxsize=32)
    def get_layer_offsets(self, layer: int) -> tuple[int, int]:
        return self._tmxdata.layers[layer].offsetx, self._tmxdata.layers[layer].offsety

    @lru_cache(maxsize=1)
    def get_1f_layer_id(self) -> int:
        for layer in self._tmxdata.layers:
            if layer.name == "1f":
                return layer.id
        return None

    def get_ground_layer_ids(self) -> list[int]:
        groundlayernames: str | None = self._tmxdata.properties.get("GroundLayerNames")
        if not groundlayernames:
            return []
        return [
            self._tmxdata.get_layer_by_name(layer_name)
            for layer_name in groundlayernames.split(",")
        ]

    @property
    def width(self):
        return self._tmxdata.width

    @property
    def height(self):
        return self._tmxdata.height

    @property
    def tile_height(self):
        return self._tmxdata.tileheight

    @property
    def tile_width(self):
        return self._tmxdata.tilewidth
