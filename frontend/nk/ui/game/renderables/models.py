from abc import ABC
from dataclasses import dataclass

import pygame
from pygame.sprite import Group as SpriteGroup
from pygame.surface import Surface  # pylint: disable=no-name-in-module

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
class TracerRenderable(Renderable):
    start: tuple[float, float]
    end: tuple[float, float]

    def draw(self, surface: Surface, camera: Camera):
        if not camera.is_visible(*self.start):
            return
        sx, sy = self.start
        ex, ey = self.end
        start = (sx - camera.x, sy - camera.y)
        end = (ex - camera.x, ey - camera.y)
        pygame.draw.line(surface, pygame.Color("white"), start, end)


@dataclass
class SpriteRenderable(Renderable):
    sprite_group: SpriteGroup

    def draw(self, surface: Surface, camera: Camera):
        self.sprite_group.draw(surface)
