from loguru import logger
from nk.models import WorldComponentProvider
from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.models.projectile import Projectile


class ProjectileComponent:

    def __init__(self, world: WorldComponentProvider):
        self.world = world
        self.projectiles: list[Projectile] = []

    def update(self, dt: float):
        for projectile in self.projectiles:
            projectile.update(dt)
            should_remove = False
            for query_info in self.world.space.shape_query(projectile.shape):
                if hasattr(query_info.shape.body, "character"):
                    character: Character = query_info.shape.body.character
                    # i guess there's friendly fire for now :D
                    if projectile.origin != character:
                        dmg = 1
                        character.handle_damage_received(dmg)
                        msg = builders.build_character_damaged(character, dmg)
                        self.world.broadcast(msg)
                        should_remove = True
                else:
                    should_remove = True
            if should_remove:
                self.projectiles.remove(projectile)
                msg = builders.build_projectile_destroyed(projectile.uuid)
                self.world.broadcast(msg)
                logger.debug("Projectile destroyed: {}", projectile.uuid)
