from unittest.mock import AsyncMock, Mock, patch

import pytest
from nk_shared.models.zone import EnemyGroup, Environment, Spawner, Zone

from app.ai import Ai
from app.models import Player
from app.world import World


@pytest.fixture
def player() -> Player:
    return Player(user_id="testuuid", start_x=10, start_y=0)


@pytest.fixture
def single_enemy_enemy_group() -> EnemyGroup:
    return EnemyGroup(
        character_type_str="shadow_guardian", count=1, center_x=10, center_y=0
    )


@pytest.fixture
def world(player) -> World:
    world = World()
    world.publish = AsyncMock(return_value=None)
    world.players.append(player)
    return world


@pytest.fixture
def zone(
    single_enemy_enemy_group: EnemyGroup, environment_feature: Environment
) -> Zone:
    return Zone(
        tmx_path=None,
        enemy_groups=[single_enemy_enemy_group],
        environment_features=[environment_feature],
        medics=[],
    )


@pytest.fixture
def spawner() -> Spawner:
    return Spawner(character_type_str="droid_assassin", offset_x=0, offset_y=-1)


@pytest.fixture
def environment_feature(spawner: Spawner) -> Environment:
    return Environment(
        tmx_name="factory_sm", center_x=20, center_y=0, spawners=[spawner]
    )


@pytest.fixture
def ai(world: World, zone: Zone) -> Ai:
    world._zone = zone
    return Ai(world, zone)


class TestAi:
    @pytest.mark.asyncio
    async def test_trivial_update(self, ai: Ai):
        await ai.update(0.016)

    def test_closest_player(self, ai: Ai, player: Player):
        assert ai.closest_player(0, 0) == player

    @pytest.mark.asyncio
    async def test_spawner(self, ai: Ai):
        assert len(ai.enemies) == 1
        await ai.update(10)
        assert len(ai.enemies) == 2
