from dataclasses import dataclass, field

import pygame

from nk.ui.models import GameUICalculator
from nk.ui.character_sprite import CharacterSprite
from nk_shared.models.character import Character
from nk_shared.proto import Direction
from nk_shared.util import direction_util


@dataclass
class CharacterStruct:
    character: Character
    sprite: CharacterSprite = None
    sprite_group: pygame.sprite.Group = field(default_factory=pygame.sprite.Group)
    last_moving_direction: Direction = None

    def __post_init__(self):
        if self.sprite and self.sprite not in self.sprite_group:
            self.sprite_group.add(self.sprite)


def update_character_structs(
    dt: float,
    character_structs: list[CharacterStruct],
    calculator: GameUICalculator,
):
    for character_struct in character_structs:
        character = character_struct.character
        sprite = character_struct.sprite
        if character.alive:
            if not character.attacking:
                if character.moving_direction:
                    if (
                        character.moving_direction
                        != character_struct.last_moving_direction
                    ):
                        sprite.move(
                            direction_util.to_isometric(character.moving_direction)
                        )
                    sprite.change_animation("run")
                else:
                    sprite.change_animation("idle")
            character_struct.last_moving_direction = character.facing_direction
        else:
            if sprite.sprite_name != "death":
                sprite.change_animation("death", loop=False)
        x, y = calculator.calculate_draw_coordinates(
            character.position.x,  # pylint: disable=no-member
            character.position.y,  # pylint: disable=no-member
            sprite.image,
        )
        sprite.set_position(x - calculator.cam_x, y - calculator.cam_y)
        character_struct.sprite_group.update(dt)
