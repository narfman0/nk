from nk_shared.models.character import Character
from nk_shared.proto import (
    Message,
    CharacterType,
    CharacterUpdated,
)


def build_character_update_from_character(character: Character) -> Message:
    return Message(
        character_update=CharacterUpdated(
            uuid=str(character.uuid),
            x=character.position.x,
            y=character.position.y,
            character_type=character.character_type,
            facing_direction=character.facing_direction,
            movement_direction=character.movement_direction,
        )
    )
