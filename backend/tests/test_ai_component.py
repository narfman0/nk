from unittest.mock import Mock

from nk.models import Player
from nk.ai_component import AiComponent
from nk.world import World
from nk_shared.models.zone import EnemyGroup


class TestAiComponent:
    def test_trivial_update(self):
        world = World()
        player = Player(user_id="testuuid", start_x=10, start_y=0)
        world.players.append(player)
        enemy_groups = [
            EnemyGroup(
                character_type_str="shadow_guardian", count=1, center_x=10, center_y=0
            )
        ]
        zone = Mock(enemy_groups=enemy_groups)
        ai = AiComponent(world, zone)
        ai.update(0.016)
