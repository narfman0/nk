from nk.world import World


class TestWorld:
    def test_trivial_update(self):
        world = World()
        world.update(0.016)
