from nk.util.math import cartesian_to_isometric
from nk.world import World


class Camera:  # pylint: disable=too-few-public-methods
    def __init__(self, world: World):
        self.world = world
        self.x = 0.0
        self.y = 0.0

    def update(self) -> tuple[float, float]:
        self.x, self.y = cartesian_to_isometric(
            self.world.player.position.x * self.world.map.tile_width // 2,
            self.world.player.position.y * self.world.map.tile_width // 2,
        )
        return self.x, self.y
