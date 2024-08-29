from nk.game.world import World
from nk.util.math import cartesian_to_isometric


class Camera:
    def __init__(self, world: World, screen_width: int, screen_height: int):
        self.world = world
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0.0
        self.y = 0.0
        self.tw = self.world.map.tile_width
        self.tw2 = self.tw // 2

    def update(self) -> tuple[float, float]:
        self.x, self.y = cartesian_to_isometric(
            self.world.player.position.x * self.tw2,
            self.world.player.position.y * self.tw2,
        )
        return self.x, self.y

    def is_visible(self, blit_x, blit_y) -> bool:
        # pylint: disable=chained-comparison
        sx = blit_x - self.x
        sy = blit_y - self.y
        return (
            sx < self.screen_width + self.tw
            and sx > -self.tw
            and sy < self.screen_height + self.tw
            and sy > -self.tw
        )

    def update_screen_width_height(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
