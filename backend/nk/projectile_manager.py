from functools import lru_cache
from math import cos, sin
from uuid import uuid4

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.models.attack_profile import AttackProfile
from nk_shared.models.character import Character
from nk_shared.models.projectile import Projectile

from nk.models import WorldComponentProvider
from nk.settings import DATA_ROOT


class ProjectileManager:

    def __init__(self, world: WorldComponentProvider):
        self.world = world
        self.projectiles: list[Projectile] = []

    def update(self, dt: float):
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if self.handle_projectile_collisions(projectile):
                self.projectiles.remove(projectile)
                msg = builders.build_projectile_destroyed(projectile.uuid)
                self.world.broadcast(msg)
                logger.debug("Projectile destroyed: {}", projectile.uuid)

    def handle_projectile_collisions(self, projectile: Projectile) -> bool:
        """Handle collisions for a single projectile."""
        for query_info in self.world.space.shape_query(projectile.shape):
            if hasattr(query_info.shape.body, "character"):
                character: Character = query_info.shape.body.character
                if projectile.origin != character:
                    dmg = 1
                    character.handle_damage_received(dmg)
                    msg = builders.build_character_damaged(character, dmg)
                    self.world.broadcast(msg)
                    return True
            else:
                return True
        return False

    def create_projectile(self, character: Character):
        attack_profile = self.get_attack_profile_by_name(character.attack_profile_name)
        speed = pymunk.Vec2d(
            cos(character.attack_direction), sin(character.attack_direction)
        ).scale_to_length(attack_profile.speed)
        projectile = Projectile(
            x=character.position.x + attack_profile.emitter_offset_x,
            y=character.position.y + attack_profile.emitter_offset_y,
            dx=speed.x,
            dy=speed.y,
            origin=character,
            attack_profile=attack_profile,
            attack_profile_name=attack_profile.name,
            uuid=str(uuid4()),
        )
        self.projectiles.append(projectile)
        return projectile

    @lru_cache
    def get_attack_profile_by_name(self, attack_profile_name: str) -> AttackProfile:
        path = f"{DATA_ROOT}/attack_profiles/{attack_profile_name}.yml"
        return AttackProfile.from_yaml_file(path)
