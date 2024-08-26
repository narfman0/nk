from math import cos, sin
from uuid import uuid4

import pymunk
from loguru import logger
from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.models.projectile import Projectile
from nk_shared.models.weapon import load_weapon_by_name

from app.models import WorldComponentProvider


class ProjectileManager:

    def __init__(self, world: WorldComponentProvider):
        self.world = world
        self.projectiles: list[Projectile] = []

    async def update(self, dt: float):
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if await self.handle_projectile_collisions(projectile):
                self.projectiles.remove(projectile)
                msg = builders.build_projectile_destroyed(projectile.uuid)
                await self.world.publish(msg)

    async def handle_projectile_collisions(self, projectile: Projectile) -> bool:
        """Handle collisions for a single projectile."""
        for query_info in self.world.space.shape_query(projectile.shape):
            if hasattr(query_info.shape.body, "character"):
                character: Character = query_info.shape.body.character
                if projectile.origin != character:
                    dmg = 1
                    character.handle_damage_received(dmg)
                    msg = builders.build_character_damaged(character, dmg)
                    await self.world.publish(msg)
                    return True
            else:
                return True
        return False

    def create_projectile(self, character: Character):
        weapon = load_weapon_by_name(character.weapon_name)
        speed = pymunk.Vec2d(
            cos(character.attack_direction), sin(character.attack_direction)
        ).scale_to_length(weapon.projectile_speed)
        projectile = Projectile(
            x=character.position.x,
            y=character.position.y,
            dx=speed.x,
            dy=speed.y,
            origin=character,
            weapon=weapon,
            weapon_name=character.weapon_name,
            uuid=str(uuid4()),
        )
        self.projectiles.append(projectile)
        return projectile
