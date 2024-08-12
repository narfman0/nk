from abc import ABC, abstractmethod

import pygame

from nk.ui.game.camera import Camera


class GameUICalculator(ABC):
    @abstractmethod
    def calculate_draw_coordinates(
        self,
        x: float,
        y: float,
        image: pygame.Surface,
    ) -> tuple[float, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def camera(self) -> Camera:
        raise NotImplementedError
