from nk_shared.models.character import Character
from nk_shared import proto


def build_character_attacked(character: Character) -> proto.Message:
    return proto.Message(
        character_attacked=proto.CharacterAttacked(
            uuid=str(character.uuid),
        )
    )


def build_character_damaged(character: Character, damage: float) -> proto.Message:
    return proto.Message(
        character_damaged=proto.CharacterDamaged(
            uuid=str(character.uuid),
            damage=damage,
        )
    )


def build_character_updated(character: Character) -> proto.Message:
    return proto.Message(
        character_updated=proto.CharacterUpdated(
            uuid=str(character.uuid),
            x=character.position.x,
            y=character.position.y,
            character_type=character.character_type,
            facing_direction=character.facing_direction,
            moving_direction=character.moving_direction,
        )
    )
