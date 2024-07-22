from dataclasses import dataclass

from pygame.surface import Surface
from pygame.sprite import Group as SpriteGroup
from sortedcontainers import SortedKeyList


@dataclass
class Renderable:
    key: float

    def draw(self, surface: Surface):
        pass


@dataclass
class BlittableRenderable(Renderable):
    blit_image: Surface
    blit_coords: tuple[float, float]

    def draw(self, surface: Surface):
        surface.blit(self.blit_image, self.blit_coords)


@dataclass
class SpriteRenderable(Renderable):
    sprite_group: SpriteGroup

    def draw(self, surface: Surface):
        self.sprite_group.draw(surface)


@dataclass
class MapRenderable:
    layer: int
    blit_image: Surface
    blit_coords: tuple[float, float]

    def draw(self, surface: Surface):
        surface.blit(self.blit_image, self.blit_coords)


def renderables_key(a: Renderable):
    return a.key


def renderables_generate_key(layer: int, bottom_y: float):
    return (layer << 16) + int(bottom_y)


def create_renderable_list():
    return SortedKeyList(key=renderables_key)
