from nk_shared.models.character import Character

from nk.projectile_component import ProjectileComponent
from nk.world import World


class TestProjectileComponent:
    def test_create_projectile(self):
        world = World()
        component = ProjectileComponent(world)
        component.update(0.016)
        character = Character()
        component.create_projectile(character)
        component.update(0.016)
