import numpy as np

from nk_shared.map.math import perlin


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
