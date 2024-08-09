from nk.world import World


def test_get_character_by_uuid(world: World):
    result = world.get_character_by_uuid("1234")
    assert result.uuid == "1234"

    result = world.get_character_by_uuid("789")
    assert result is None
