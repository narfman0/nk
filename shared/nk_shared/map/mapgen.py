import os
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, cKDTree, voronoi_plot_2d

from nk_shared.map.helpers import (
    create_elevation as create_elevation_helper,
    generate_tilemap,
)
from nk_shared.map.helpers import get_perimeter_points
from nk_shared.map.math import lloyds_algorithm
from nk_shared.map.tiled import write_tmx_file
from nk_shared.settings import MAPGEN_WIDTH, PROJECT_ROOT


def create_points(count: int, width: int) -> np.ndarray:
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


def create_elevation(width: int, visualize: bool) -> np.ndarray:
    start = time.time()
    p = create_elevation_helper(width)
    end = time.time()
    print(f"Elevations: {end - start:.2f}s")
    if visualize:
        plt.imshow(p, origin="upper")
        plt.show()
    return p


def get_perimeter_regions(width: int, points: np.ndarray) -> tuple[np.ndarray, cKDTree]:
    start = time.time()
    voronoi_kdtree = cKDTree(points)
    # get test points around perimeter
    perimeter_points = get_perimeter_points(width)
    # use test points to get all edge regions
    _test_point_dist, perimeter_regions = voronoi_kdtree.query(perimeter_points, k=1)
    perimeter_regions = np.unique(perimeter_regions)
    end = time.time()
    print(f"Perimeter regions: {end-start:.2f}s. {len(perimeter_regions)} regions")
    return perimeter_regions, voronoi_kdtree


def generate_map(point_count: int, width: int, visualize: bool = False):
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    np.random.seed(0)
    points = create_points(point_count, width)
    # create_voronoi(points, visualize)
    # p = create_elevation()
    perimeter_regions, voronoi_kdtree = get_perimeter_regions(width, points)
    tilemap = generate_tilemap(perimeter_regions, voronoi_kdtree, width)
    # TODO
    # flood fill lower 10% of regions with water from elevation map
    # fill top 15% with snow
    # fill far from water with dirt
    write_tmx_file(tilemap)


if __name__ == "__main__":
    generate_map(MAPGEN_WIDTH // 10, MAPGEN_WIDTH, True)
