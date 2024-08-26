# pylint: disable=no-member
from enum import Enum, auto

import pygame
from nk_shared.proto import Direction
from pygame.event import Event


class ActionEnum(Enum):
    DASH = auto()
    ATTACK = auto()
    PLAYER_HEAL = auto()
    PLAYER_INVICIBILITY = auto()
    ZOOM_OUT = auto()
    ZOOM_IN = auto()
    RELOAD = auto()


def read_input_player_move_direction():
    keys = pygame.key.get_pressed()
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    up = keys[pygame.K_UP] or keys[pygame.K_w]
    down = keys[pygame.K_DOWN] or keys[pygame.K_s]
    direction = None
    if down:
        if right:
            direction = Direction.DIRECTION_E
        elif left:
            direction = Direction.DIRECTION_S
        else:
            direction = Direction.DIRECTION_SE
    elif up:
        if right:
            direction = Direction.DIRECTION_N
        elif left:
            direction = Direction.DIRECTION_W
        else:
            direction = Direction.DIRECTION_NW
    elif left:
        direction = Direction.DIRECTION_SW
    elif right:
        direction = Direction.DIRECTION_NE
    return direction


def read_input_player_actions(events: list[Event]) -> list[ActionEnum]:
    actions = []
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                actions.append(ActionEnum.DASH)
            elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                actions.append(ActionEnum.ATTACK)
            elif event.key == pygame.K_F2:
                actions.append(ActionEnum.PLAYER_HEAL)
            elif event.key == pygame.K_F3:
                actions.append(ActionEnum.PLAYER_INVICIBILITY)
            elif event.key == pygame.K_r:
                actions.append(ActionEnum.RELOAD)
        if event.type == pygame.MOUSEWHEEL:
            if event.y < 0:
                actions.append(ActionEnum.ZOOM_OUT)
            else:
                actions.append(ActionEnum.ZOOM_IN)
    if pygame.mouse.get_pressed()[0]:
        actions.append(ActionEnum.ATTACK)
    return actions
