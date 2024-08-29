from nk_shared import proto
from nk_shared.models import Character
from nk_shared.proto import Projectile


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
