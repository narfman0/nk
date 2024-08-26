from math import cos, sin
from typing import Protocol
from uuid import uuid4

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.models import Character, Projectile
from nk_shared.models.weapon import load_weapon_by_name
from nk_shared.proto import Projectile as ProjectileProto
from nk_shared.proto import ProjectileCreated


class WorldProtocol(Protocol):
    @property
    def space(self) -> pymunk.Space:
        pass

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        pass


class ProjectileManager:
    def __init__(self, world: WorldProtocol):
        self.world = world
        self.projectiles: list[Projectile] = []

    def update(self, dt: float):
        for projectile in self.projectiles:
            projectile.update(dt)
            if self.handle_projectile_collisions(projectile):
                self.projectiles.remove(projectile)

    def process_local_attack(self, character: Character) -> ProjectileCreated:
        weapon = load_weapon_by_name(character.weapon_name)
        speed = pymunk.Vec2d(
            cos(character.attack_direction), sin(character.attack_direction)
        ).scale_to_length(weapon.speed)
        projectile = ProjectileProto(
            uuid=str(uuid4()),
            x=character.position.x + weapon.emitter_offset_x,
            y=character.position.y + weapon.emitter_offset_y,
            dx=speed.x,
            dy=speed.y,
            weapon_name=character.weapon_name,
        )
        proto = builders.build_projectile_created(character, projectile)
        self.create_projectile(proto.projectile_created)

    def handle_projectile_collisions(self, projectile: Projectile) -> bool:
        """Handle collisions for a single projectile."""
        for query_info in self.world.space.shape_query(projectile.shape):
            # pylint: disable-next=no-else-return
            if hasattr(query_info.shape.body, "character"):
                character: Character = query_info.shape.body.character
                return projectile.origin != character
            else:
                return True
        return False

    def create_projectile(self, proto: ProjectileCreated):
        weapon = load_weapon_by_name(proto.projectile.weapon_name)
        self.projectiles.append(
            Projectile(
                origin=self.world.get_character_by_uuid(proto.origin_uuid),
                uuid=proto.projectile.uuid,
                weapon=weapon,
                x=proto.projectile.x,
                y=proto.projectile.y,
                dx=proto.projectile.dx,
                dy=proto.projectile.dy,
            )
        )
        logger.debug("Created projectile: {}", self.projectiles[-1])

    def get_projectile_by_uuid(self, uuid: str) -> Projectile | None:
        for projectile in self.projectiles:
            if projectile.uuid == uuid:
                return projectile
        return None
