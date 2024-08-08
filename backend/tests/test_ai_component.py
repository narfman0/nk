from unittest.mock import Mock
from nk.ai_component import AiComponent


class TestAiComponent:
    def test_main(self):
        world_mock = Mock()
        zone_mock = Mock(enemy_groups=[])
        ai = AiComponent(world_mock, zone_mock)
        ai.update(0.016)
