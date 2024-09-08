import os
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, cKDTree, voronoi_plot_2d

from nk_shared.settings import PROJECT_ROOT, MAP_WIDTH
from nk_shared.map.math import lloyds_algorithm
from nk_shared.map.helpers import (
    get_perimeter_points,
    create_elevation as create_elevation_helper,
)


def create_points(width: int) -> np.array:
    start = time.time()
    points = lloyds_algorithm(np.random.rand(width, 2) * width, 4)
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


def generate_map(width: int, visualize: bool = False):
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    np.random.seed(0)
    points = create_points(width)
    # vor = create_voronoi(points, visualize)
    # p = create_elevation()
    perimeter_regions = get_perimeter_regions(width, points)
    # TODO
    # mark edge regions as water
    # flood fill lower 10% of regions with water from elevation map
    # generate a 2d grid of test points equidistant from each other
    # figure out moisture levels for each region
    #   - moisture levels are based on distance from water
    #   - might need to build a graph of regions to determine distance


if __name__ == "__main__":
    generate_map(MAP_WIDTH, False)
