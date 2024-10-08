from dataclasses import dataclass, field

import pygame
from nk_shared import direction_util
from nk_shared.models.character import Character
from nk_shared.proto import Direction

from nk.ui.game.character_sprite import CharacterSprite
from nk.ui.game.models import UIInterface


@dataclass
class CharacterStruct:
    character: Character
    sprite: CharacterSprite = None
    sprite_group: pygame.sprite.Group = field(default_factory=pygame.sprite.Group)
    last_moving_direction: Direction = None

    def __post_init__(self):
        if self.sprite and self.sprite not in self.sprite_group:
            self.sprite_group.add(self.sprite)


@dataclass
class CharacterStructRemoveStruct:
    character_struct: CharacterStruct
    time_until_removal: float


def update_position(
    character: Character, sprite: CharacterSprite, ui_interface: UIInterface
):
    x, y = ui_interface.calculate_draw_coordinates(
        character.position.x,  # pylint: disable=no-member
        character.position.y,  # pylint: disable=no-member
        sprite.image,
    )
    sprite.set_position(x - ui_interface.camera.x, y - ui_interface.camera.y)


def update_animation(
    character: Character, sprite: CharacterSprite, character_struct: CharacterStruct
):
    if character.alive:
        if not character.attacking:
            if character.moving_direction:
                if character.moving_direction != character_struct.last_moving_direction:
                    sprite.move(direction_util.to_isometric(character.moving_direction))
                sprite.change_animation("run")
            else:
                sprite.change_animation("idle")
        character_struct.last_moving_direction = character.facing_direction
    else:
        if sprite.sprite_name != "death":
            sprite.change_animation("death", loop=False)


def update_character_structs(
    dt: float,
    character_structs: dict[str, CharacterStruct],
    ui_interface: UIInterface,
):
    for character_struct in character_structs.values():
        character = character_struct.character
        sprite = character_struct.sprite
        update_animation(character, sprite, character_struct)
        update_position(character, sprite, ui_interface)
        character_struct.sprite_group.update(dt)
