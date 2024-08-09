from unittest.mock import Mock

import pytest

from nk.models import Player
from nk.ai_component import AiComponent
from nk.world import World
from nk_shared.models.zone import EnemyGroup


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
    world.players.append(player)
    return world


@pytest.fixture
def zone(single_enemy_enemy_group) -> AiComponent:
    return Mock(enemy_groups=[single_enemy_enemy_group], environment_features=[])


@pytest.fixture
def ai(world, zone) -> AiComponent:
    return AiComponent(world, zone)


class TestAiComponent:
    def test_trivial_update(self, ai: AiComponent):
        ai.update(0.016)

    def test_closest_player(self, ai: AiComponent, player: Player):
        assert ai.closest_player(0, 0) == player
