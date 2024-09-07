import os
import time

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from lloyd import Field
from scipy.spatial import Voronoi, voronoi_plot_2d

from nk_shared.settings import PROJECT_ROOT

DEFUALT_WIDTH = 100


def generate_points(width: int = DEFUALT_WIDTH, relax_steps: int = 4) -> np.array:
    points = np.random.rand(width, 2) * width
    field = Field(points)
    for _ in range(relax_steps):
        field.relax()
    return field.get_points()


def create_diagram():
    vor = Voronoi(generate_points())
    fig: Figure = voronoi_plot_2d(vor)
    fig.savefig(f"{PROJECT_ROOT}/output/scipy_final.png")


if __name__ == "__main__":
    start = time.time()
    if not os.path.exists(f"{PROJECT_ROOT}/output"):
        os.mkdir(f"{PROJECT_ROOT}/output")
    create_diagram()
    end = time.time()
    print(f"Mapgen time: {end - start:.2f}s")
    plt.show()
