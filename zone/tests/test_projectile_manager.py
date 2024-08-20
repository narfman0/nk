import pytest
from nk_shared.models.character import Character

from app.projectile_manager import ProjectileManager
from app.world import World


@pytest.fixture
def projectile_manager(world) -> ProjectileManager:
    return ProjectileManager(world)


@pytest.fixture
def world() -> World:
    return World()


class TestProjectileManager:
    @pytest.mark.asyncio
    async def test_create_projectile(self, projectile_manager: ProjectileManager):
        character = Character()
        projectile_manager.create_projectile(character)
        await projectile_manager.update(0.016)
