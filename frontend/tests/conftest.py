from unittest.mock import Mock, patch
import pytest
import pytmx

from nk_shared.map import DATA_ROOT

from nk.world import World, Projectile


@pytest.fixture
def map_headless():
    with patch("nk_shared.map.pytmx.load_pygame") as load_pygame_mock:
        load_pygame_mock.return_value = pytmx.TiledMap(f"{DATA_ROOT}/tiled/tmx/1.tmx")
        yield


@pytest.fixture
def world(map_headless) -> World:
    return World(uuid="1234", x=0, y=0)


@pytest.fixture
def projectile_proto() -> Projectile:
    return Projectile(
        uuid="abcde", attack_profile_name="laserball", x=0, y=0, dx=1, dy=1
    )
