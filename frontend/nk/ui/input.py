from enum import Enum

import pygame
from pygame.event import Event

from nk_shared.models.direction import Direction


class ActionEnum(Enum):
    DASH = 1
    ATTACK = 2
    PLAYER_HEAL = 4
    PLAYER_INVICIBILITY = 5
    ZOOM_OUT = 6
    ZOOM_IN = 7
    HELLO_WORLD_NET = 8


def read_input_player_move_direction():
    keys = pygame.key.get_pressed()
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    up = keys[pygame.K_UP] or keys[pygame.K_w]
    down = keys[pygame.K_DOWN] or keys[pygame.K_s]
    direction = None
    if down:
        if right:
            direction = Direction.E
        elif left:
            direction = Direction.S
        else:
            direction = Direction.SE
    elif up:
        if right:
            direction = Direction.N
        elif left:
            direction = Direction.W
        else:
            direction = Direction.NW
    elif left:
        direction = Direction.SW
    elif right:
        direction = Direction.NE
    return direction


def read_input_player_actions(events: list[Event]) -> list[ActionEnum]:
    actions = []
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                actions.append(ActionEnum.DASH)
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                actions.append(ActionEnum.ATTACK)
            elif event.key == pygame.K_F2:
                actions.append(ActionEnum.PLAYER_HEAL)
            elif event.key == pygame.K_F3:
                actions.append(ActionEnum.PLAYER_INVICIBILITY)
            elif event.key == pygame.K_h:
                actions.append(ActionEnum.HELLO_WORLD_NET)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                actions.append(ActionEnum.ATTACK)
        if event.type == pygame.MOUSEWHEEL:
            if event.y < 0:
                actions.append(ActionEnum.ZOOM_OUT)
            else:
                actions.append(ActionEnum.ZOOM_IN)
    return actions
