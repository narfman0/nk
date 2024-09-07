import os
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

from nk_shared.settings import PROJECT_ROOT
from nk_shared.map.math import lloyds_algorithm, perlin

DEFAULT_WIDTH = 1000


def generate_points(width: int = DEFAULT_WIDTH, relax_steps: int = 4) -> np.array:
    return lloyds_algorithm(np.random.rand(width, 2) * width, relax_steps)


def create_elevation(width: int = DEFAULT_WIDTH) -> np.array:
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


if __name__ == "__main__":
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    np.random.seed(0)

    start = time.time()
    vor = Voronoi(generate_points())
    end = time.time()
    print(f"Voronoi time: {end - start:.2f}s")
    voronoi_plot_2d(vor)
    plt.show()

    start = time.time()
    p = create_elevation()
    end = time.time()
    plt.imshow(p, origin="upper")
    print(f"Elevations time: {end - start:.2f}s")
    plt.show()
