import pytest
from nk_shared.map import Tilemap
from nk_shared.proto import Projectile

from nk.game.world import World


@pytest.fixture
def tmxmap():
    return Tilemap("1", headless=True)


@pytest.fixture
def world(tmxmap) -> World:
    return World(uuid="1234", x=0, y=0, tmxmap=tmxmap)


@pytest.fixture
def projectile_proto() -> Projectile:
    return Projectile(uuid="abcde", weapon_name="laserball", x=0, y=0, dx=1, dy=1)
