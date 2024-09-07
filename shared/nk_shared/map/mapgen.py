import os
import time

from matplotlib.figure import Figure
import numpy as np
from lloyd import Field
from foronoi import Voronoi, BoundingBox, VoronoiObserver

DEFUALT_WIDTH = 100


def generate_points(width: int = DEFUALT_WIDTH, relax_steps: int = 10) -> np.array:
    points = np.random.rand(width, 2) * width
    field = Field(points)
    for _ in range(relax_steps):
        field.relax()
    return field.get_points()


def observer_callback(observer: VoronoiObserver, figure: Figure):
    if observer.n_messages % 10 == 0:
        figure.savefig(f"output/{observer.n_messages:02d}.png")


def create_diagram() -> Voronoi:
    v = Voronoi(BoundingBox(0, DEFUALT_WIDTH, 0, DEFUALT_WIDTH))
    v.attach_observer(
        VoronoiObserver(
            settings=dict(
                polygon=True,
                edges=True,
                vertices=True,
                sites=True,
                outgoing_edges=False,
                border_to_site=False,
                scale=1,
                edge_labels=False,
                site_labels=False,
                triangles=False,
                arcs=False,
            ),
            callback=observer_callback,
        )
    )
    v.create_diagram(points=generate_points())
    return v


if __name__ == "__main__":
    start = time.time()
    if not os.path.exists("output"):
        os.mkdir("output")
    create_diagram()
    end = time.time()
    print(f"Mapgen time: {end - start:.2f}s")
