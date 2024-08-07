import random
from math import atan2

from nk_shared import builders
from nk_shared.models.zone import Zone
from nk_shared.proto import CharacterType
from nk_shared.util import direction_util

from nk.models import Enemy, WorldComponentProvider

UPDATE_FREQUENCY = 0.1


class AiComponent:

    def __init__(self, world: WorldComponentProvider, zone: Zone):
        self.world = world
        self.zone = zone
        self.next_update_time = 0
        self.enemies: list[Enemy] = []
        for enemy_group in self.zone.enemy_groups:
            r = 1 + enemy_group.count // 2  # randomize where group is centered
            for _ in range(enemy_group.count):
                self.spawn_enemy(
                    enemy_group.character_type,
                    enemy_group.center_x + random.randint(-r, r),
                    enemy_group.center_y + random.randint(-r, r),
                )

    def update(self, dt: float):
        """Update enemy behaviors. Long term refactor option (e.g. behavior trees)"""
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                enemy.moving_direction = None
                player = self.world.closest_player(enemy.position.x, enemy.position.y)
                if not player:
                    continue
                player_dst_sqrd = enemy.position.get_dist_sqrd(player.position)
                if player_dst_sqrd < enemy.chase_distance**2:
                    enemy.moving_direction = direction_util.direction_to(
                        enemy.position, player.position
                    )
                if player_dst_sqrd < enemy.attack_distance**2 and not enemy.attacking:
                    direction = atan2(
                        player.position.y - enemy.position.y,
                        player.position.x - enemy.position.x,
                    )
                    enemy.attack(direction)
                    self.world.broadcast(
                        builders.build_character_attacked(enemy, direction)
                    )
                self.world.broadcast(builders.build_character_updated(enemy))

    def spawn_enemy(
        self, character_type: CharacterType, center_x: int, center_y: int
    ) -> Enemy:
        character = Enemy(
            character_type=character_type,
            center_y=center_y,
            center_x=center_x,
            start_x=center_x,
            start_y=center_y,
        )
        self.enemies.append(character)
        self.world.handle_character_created(character)
        return character
