from nk_shared.models import Character, Projectile
from nk_shared import proto


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
        )
    )


def build_character_updated(character: Character) -> proto.Message:
    return proto.Message(
        character_updated=proto.CharacterUpdated(
            uuid=character.uuid,
            x=character.body.position.x,
            y=character.body.position.y,
            dx=character.body.velocity.x,
            dy=character.body.velocity.y,
            character_type=character.character_type,
            facing_direction=character.facing_direction,
            moving_direction=character.moving_direction,
        )
    )


def build_projectile_created(projectile: Projectile) -> proto.Message:
    return proto.Message(
        projectile_created=proto.ProjectileCreated(
            projectile=build_projectile(projectile)
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
        attack_profile_name=projectile.attack_profile_name,
    )
