from abc import ABC
from dataclasses import dataclass

from pygame.sprite import Group as SpriteGroup
from pygame.surface import Surface  # pylint: disable=no-name-in-module
from sortedcontainers import SortedKeyList

from nk.ui.game.camera import Camera


@dataclass
class Renderable(ABC):
    key: float

    def draw(self, surface: Surface, camera: Camera):
        raise NotImplementedError


@dataclass
class BlittableRenderable(Renderable):
    blit_image: Surface
    blit_coords: tuple[float, float]

    def draw(self, surface: Surface, camera: Camera):
        if not camera.is_visible(*self.blit_coords):
            return
        x, y = self.blit_coords
        surface.blit(self.blit_image, (x - camera.x, y - camera.y))


@dataclass
class SpriteRenderable(Renderable):
    sprite_group: SpriteGroup

    def draw(self, surface: Surface, camera: Camera):
        self.sprite_group.draw(surface)


def renderables_key(a: Renderable):
    return a.key


def renderables_generate_key(layer: int, bottom_y: float):
    return (layer << 16) + int(bottom_y)


def create_renderable_list():
    return SortedKeyList(key=renderables_key)
