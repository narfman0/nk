import os
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, cKDTree, voronoi_plot_2d

from nk_shared.map.helpers import create_elevation as create_elevation_helper
from nk_shared.map.helpers import get_perimeter_points
from nk_shared.map.math import lloyds_algorithm
from nk_shared.map.models import Biome
from nk_shared.settings import MAP_WIDTH, PROJECT_ROOT

BIOME_TO_TILE_IDS = {
    Biome.PLAINS: [32, 33, 34, 35],
    Biome.WATER: [100, 101, 102, 103],
}


def create_points(count: int, width: int) -> np.array:
    start = time.time()
    points = lloyds_algorithm(np.random.rand(count, 2) * width, 4)
    end = time.time()
    print(f"Generate points + Lloyd's: {end - start:.2f}s")
    return points


def create_voronoi(points: np.array, visualize: bool) -> Voronoi:
    start = time.time()
    vor = Voronoi(points)
    end = time.time()
    print(f"Voronoi: {end - start:.2f}s")
    if visualize:
        voronoi_plot_2d(vor)
        plt.show()
    return vor


def create_elevation(width: int, visualize: bool) -> np.array:
    start = time.time()
    p = create_elevation_helper(width)
    end = time.time()
    print(f"Elevations: {end - start:.2f}s")
    if visualize:
        plt.imshow(p, origin="upper")
        plt.show()
    return p


def get_perimeter_regions(width: int, points: np.array) -> np.array:
    start = time.time()
    voronoi_kdtree = cKDTree(points)
    # get test points around perimeter
    perimeter_points = get_perimeter_points(width)
    # use test points to get all edge regions
    _test_point_dist, perimeter_regions = voronoi_kdtree.query(perimeter_points, k=1)
    perimeter_regions = np.unique(perimeter_regions)
    end = time.time()
    print(f"Perimeter regions: {end-start:.2f}s. {len(perimeter_regions)} regions")
    return perimeter_regions


def generate_tilemap(perimeter_regions: np.array, width: int) -> np.array:
    # lets set perimeter regions to water, everything else to land
    grid = np.zeros((width, width))
    for x in range(width):
        for y in range(width):
            biome = (
                Biome.WATER
                if x in perimeter_regions or y in perimeter_regions
                else Biome.PLAINS
            )
            tiled_id = np.random.choice(BIOME_TO_TILE_IDS[biome])
            grid[x, y] = tiled_id
    return grid


def generate_tiled_tmx(width: int, tilemap: np.array):
    lines = []
    for x in range(width):
        line_arr = []
        for y in range(width):
            line_arr.append(str(int(tilemap[x, y])))
        lines.append(",".join(line_arr))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.10.2" orientation="isometric" renderorder="right-down" width="{width}" height="{width}" tilewidth="32" tileheight="16" infinite="0" nextlayerid="10" nextobjectid="1">
 <properties>
  <property name="StartXY" value="45,30"/>
 </properties>
 <tileset firstgid="0" source="../tsx/jumpstart.tsx"/>
 <layer id="1" name="1" width="{width}" height="{width}" offsetx="0" offsety="0">
  <data encoding="csv">
{",\n".join(lines)}
</data>
 </layer>
</map>"""


def generate_map(point_count: int, width: int, visualize: bool = False):
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    np.random.seed(0)
    points = create_points(point_count, width)
    # create_voronoi(points, visualize)
    # p = create_elevation()
    perimeter_regions = get_perimeter_regions(width, points)
    tilemap = generate_tilemap(perimeter_regions, width)
    with open(f"{PROJECT_ROOT}/output/map.tmx", "w", encoding="utf-8") as f:
        f.write(generate_tiled_tmx(width, tilemap))

    # TODO
    # mark edge regions as water
    # flood fill lower 10% of regions with water from elevation map
    # generate a 2d grid of test points equidistant from each other
    # figure out moisture levels for each region
    #   - moisture levels are based on distance from water
    #   - might need to build a graph of regions to determine distance


if __name__ == "__main__":
    generate_map(MAP_WIDTH // 10, MAP_WIDTH, True)
