from abc import ABC, abstractmethod, abstractproperty

import pygame


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
    def cam_x(self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def cam_y(self) -> float:
        raise NotImplementedError
