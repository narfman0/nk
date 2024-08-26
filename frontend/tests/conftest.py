import pytest
from nk_shared.map import Map
from nk_shared.proto import Projectile

from nk.game.world import World


@pytest.fixture
def map():
    return Map("1", headless=True)


@pytest.fixture
def world(map) -> World:
    return World(uuid="1234", x=0, y=0, map=map)


@pytest.fixture
def projectile_proto() -> Projectile:
    return Projectile(uuid="abcde", weapon_name="laserball", x=0, y=0, dx=1, dy=1)
