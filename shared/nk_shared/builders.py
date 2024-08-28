from nk_shared import proto
from nk_shared.models import Character
from nk_shared.proto import Projectile


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


def build_player_disconnected(uuid: str) -> proto.Message:
    return proto.Message(player_disconnected=proto.PlayerDisconnected(uuid=uuid))


def build_player_respawned(character: Character) -> proto.Message:
    return proto.Message(
        player_respawned=proto.PlayerRespawned(
            uuid=character.uuid,
            x=character.position.x,
            y=character.position.y,
        ),
    )


def build_projectile_created(
    origin: Character, projectile: Projectile
) -> proto.Message:
    return proto.Message(
        projectile_created=proto.ProjectileCreated(
            origin_uuid=origin.uuid, projectile=build_projectile(projectile)
        )
    )


def build_projectile_destroyed(uuid: str) -> proto.Message:
    return proto.Message(projectile_destroyed=proto.ProjectileDestroyed(uuid=uuid))


def build_projectile(projectile: Projectile) -> proto.Message:
    return proto.Projectile(
        uuid=projectile.uuid,
        x=projectile.x,
        y=projectile.y,
        dx=projectile.dx,
        dy=projectile.dy,
        weapon_name=projectile.weapon_name,
    )
