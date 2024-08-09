from unittest.mock import Mock

import pytest
from nk_shared.models.zone import EnemyGroup

from nk.ai import Ai
from nk.models import Player
from nk.world import World


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
def zone(single_enemy_enemy_group) -> Ai:
    return Mock(enemy_groups=[single_enemy_enemy_group], environment_features=[])


@pytest.fixture
def ai(world, zone) -> Ai:
    return Ai(world, zone)


class TestAi:
    def test_trivial_update(self, ai: Ai):
        ai.update(0.016)

    def test_closest_player(self, ai: Ai, player: Player):
        assert ai.closest_player(0, 0) == player
