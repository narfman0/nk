import os
import time

from loguru import logger
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, cKDTree, voronoi_plot_2d

from nk_shared.settings import PROJECT_ROOT
from nk_shared.map.math import lloyds_algorithm, perlin

WIDTH = 1000


def create_elevation(width: int = WIDTH) -> np.array:
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


def generate_map(visualize: bool = False):
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    np.random.seed(0)

    start = time.time()
    points = lloyds_algorithm(np.random.rand(WIDTH, 2) * WIDTH, 4)
    end = time.time()
    print(f"Generate points + Lloyd's: {end - start:.2f}s")

    start = time.time()
    vor = Voronoi(points)
    end = time.time()
    print(f"Voronoi: {end - start:.2f}s")
    if visualize:
        voronoi_plot_2d(vor)
        plt.show()

    start = time.time()
    p = create_elevation()
    end = time.time()
    print(f"Elevations: {end - start:.2f}s")
    if visualize:
        plt.imshow(p, origin="upper")
        plt.show()

    voronoi_kdtree = cKDTree(points)
    test_points = np.random.rand(100, 2) * WIDTH
    _test_point_dist, test_point_regions = voronoi_kdtree.query(test_points, k=1)

    logger.info(test_point_regions)
    # TODO
    # get test points around perimeter
    # use test points to get all edge regions
    # mark edge regions as water
    # flood fill lower 10% of regions with water from elevation map
    # generate a 2d grid of test points equidistant from each other
    # figure out moisture levels for each region
    #   - moisture levels are based on distance from water
    #   - might need to build a graph of regions to determine distance


if __name__ == "__main__":
    generate_map(False)
