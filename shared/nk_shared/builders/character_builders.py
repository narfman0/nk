from nk_shared import proto
from nk_shared.models import Character


def build_character_attacked(character: Character, direction: float) -> proto.Message:
    return proto.Message(
        character_attacked=proto.CharacterAttacked(
            uuid=character.uuid,
            direction=direction,
        )
    )


def build_character_damaged(character: Character, damage: float) -> proto.Message:
    return proto.Message(
        character_damaged=proto.CharacterDamaged(
            uuid=character.uuid,
            damage=damage,
            hp=character.hp,
        )
    )


def build_character_position_updated(character: Character) -> proto.Message:
    return proto.Message(
        origin_uuid=character.uuid,
        character_position_updated=proto.CharacterPositionUpdated(
            uuid=character.uuid,
            x=character.position.x,
            y=character.position.y,
            dx=character.velocity.x,
            dy=character.velocity.y,
        ),
    )


def build_character_reloaded(character: Character) -> proto.Message:
    return proto.Message(
        character_reloaded=proto.CharacterReloaded(
            uuid=character.uuid,
        )
    )


def build_character_direction_updated(character: Character) -> proto.Message:
    return proto.Message(
        origin_uuid=character.uuid,
        character_direction_updated=proto.CharacterDirectionUpdated(
            uuid=character.uuid,
            facing_direction=character.facing_direction,
            moving_direction=character.moving_direction,
        ),
    )


def build_character_updated(character: Character) -> proto.Message:
    return proto.Message(
        origin_uuid=character.uuid,
        character_updated=proto.CharacterUpdated(
            uuid=character.uuid,
            x=character.position.x,
            y=character.position.y,
            dx=character.velocity.x,
            dy=character.velocity.y,
            character_type=character.character_type,
            facing_direction=character.facing_direction,
            moving_direction=character.moving_direction,
            hp=character.hp,
        ),
    )
