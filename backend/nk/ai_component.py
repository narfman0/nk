import random
from math import atan2

from nk_shared import builders
from nk_shared.models.zone import Zone
from nk_shared.proto import CharacterType
from nk_shared.util import direction_util

from nk.models import Enemy, Player, WorldComponentProvider

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
                player = self.closest_player(enemy.position.x, enemy.position.y)
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

    def closest_player(self, x: float, y: float) -> Player | None:
        """Retrieve the closest player to the given x,y pair.
        Long term, should considering splitting world into zone/chunks, but
        this is a scan currently."""
        closest, min_dst = None, float("inf")
        for player in self.world.get_players():
            if player.alive:
                dst = player.position.get_dist_sqrd((x, y))
                if dst < min_dst:
                    closest = player
                    min_dst = dst
        return closest

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
        self.world.space.add(character.body, character.shape, character.hitbox_shape)
        return character
