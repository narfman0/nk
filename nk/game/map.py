from functools import lru_cache

import pymunk
import pytmx


class Map:
    def __init__(self, area: str):
        self.area = area
        self._tmxdata = pytmx.load_pygame(f"data/tiled/{area}.tmx")

    def get_start_tile(self):
        return map(int, self._tmxdata.properties.get("StartXY").split(","))

    @lru_cache(maxsize=None)
    def get_tile_image(self, tile_x: int, tile_y: int, layer: int):
        return self._tmxdata.get_tile_image(tile_x, tile_y, layer)

    def get_tile_layer_count(self):
        return len(list(self._tmxdata.visible_tile_layers))

    def add_map_geometry_to_space(self, space: pymunk.Space):
        for layer in range(self.get_tile_layer_count()):
            for y in range(self.height):
                for x in range(self.width):
                    tile_props = self._tmxdata.get_tile_properties(x, y, layer) or {}
                    colliders: list = tile_props.get("colliders", [])
                    if colliders:
                        body = pymunk.Body(body_type=pymunk.Body.STATIC)
                        body.position = (0.5 + x, 0.5 + y)
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

    def get_ground_layer_ids(self) -> int:
        layer_names = self._tmxdata.properties.get("GroundLayerNames").split(",")
        return [
            self._tmxdata.get_layer_by_name(layer_name) for layer_name in layer_names
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

    @property
    @lru_cache(maxsize=1)
    def tile_half_width(self):
        return self._tmxdata.tilewidth // 2
