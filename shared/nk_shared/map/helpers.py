import time
import numpy as np
from scipy.spatial import cKDTree

from nk_shared.map.math import perlin
from nk_shared.map.models import Biome


def create_elevation(width: int) -> np.array:
    """from https://stackoverflow.com/a/42154921"""
    p = np.zeros((width, width))
    for i in range(4):
        freq = 2**i
        lin = np.linspace(0, freq, width, endpoint=False)
        x, y = np.meshgrid(
            lin, lin
        )  # FIX3: I thought I had to invert x and y here but it was a mistake
        p = perlin(x, y) / freq + p
    return p


def get_perimeter_points(width: int) -> list[tuple[int, int]]:
    return (
        [(x, 0) for x in range(width)]
        + [(0, y) for y in range(width)]
        + [(x, width - 1) for x in range(width)]
        + [(width - 1, y) for y in range(width)]
    )


BIOME_TO_TILE_IDS = {
    Biome.PLAINS: [40, 41, 42, 43],
    Biome.WATER: [100, 101, 102, 103],
}


def generate_tilemap(
    perimeter_regions: np.ndarray, voronoi_kdtree: cKDTree, width: int
) -> np.ndarray:
    # set perimeter regions to water, everything else to land
    start = time.time()
    grid = np.zeros((width, width))
    for x in range(width):
        for y in range(width):
            _dst, region = voronoi_kdtree.query((x, y), k=1)
            biome = Biome.WATER if region in perimeter_regions else Biome.PLAINS
            tiled_id = np.random.choice(BIOME_TO_TILE_IDS[biome])
            grid[x, y] = tiled_id
    end = time.time()
    print(f"Generate tilemap: {end - start:.2f}s")
    return grid
