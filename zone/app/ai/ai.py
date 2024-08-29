import random
from math import atan2, log2

from nk_shared import builders, direction_util
from nk_shared.models.character import Character
from nk_shared.models.zone import Zone
from nk_shared.proto import CharacterType, Message

from app.ai import incrementals
from app.ai.spawner_manager import SpawnerManager, SpawnerProvider
from app.models import Enemy, Player, WorldInterface, WorldListener

FULL_UPDATE_FREQUENCY = 10


class Ai(SpawnerProvider, WorldListener):
    def __init__(self, world: WorldInterface, zone: Zone):
        self.world = world
        self.zone = zone
        self.next_update_time = 0
        self.enemies: list[Enemy] = []
        self.spawn_manager = SpawnerManager(self, zone.environment_features)
        self.world.add_listener(self)
        for grp in self.zone.enemy_groups:
            self.spawn_enemies(
                grp.count, grp.character_type, grp.center_x, grp.center_y
            )

    async def update(self, dt: float):
        """Update enemy behaviors. Long term refactor option (e.g. behavior trees)"""
        if self.world.players:
            await self.spawn_manager.update(dt)

        self.next_update_time -= dt
        full_update = self.next_update_time <= 0
        if full_update:
            self.next_update_time = FULL_UPDATE_FREQUENCY
        for enemy in self.enemies:
            if enemy.alive:
                await self.update_enemy_behavior(enemy)
                if not full_update:
                    await incrementals.update_direction(self.world, enemy)
                    await incrementals.update_position(dt, self.world, enemy)
            if full_update:
                proto = builders.build_character_updated(enemy)
                await self.world.publish(proto)

    async def update_enemy_behavior(self, enemy: Enemy):
        """Update behavior for a single enemy."""
        enemy.moving_direction = None
        player = self.closest_player(enemy.position.x, enemy.position.y)
        if not player:
            return

        player_dst_sqrd = enemy.position.get_dist_sqrd(player.position)
        if player_dst_sqrd < enemy.chase_distance**2:
            enemy.moving_direction = direction_util.direction_to(
                enemy.position, player.position
            )

        if player_dst_sqrd < enemy.weapon.attack_distance**2 and not enemy.attacking:
            await self.enemy_attack(enemy, player)

    async def enemy_attack(self, enemy: Enemy, player: Player):
        """Handle enemy attack behavior."""
        direction = atan2(
            player.position.y - enemy.position.y,
            player.position.x - enemy.position.x,
        )
        enemy.attack(direction)
        await self.world.publish(builders.build_character_attacked(enemy, direction))

    def closest_player(self, x: float, y: float) -> Player | None:
        """Retrieve the closest player to the given x,y pair.
        Long term, should considering splitting world into zone/chunks, but
        this is a scan currently."""
        closest, min_dst = None, float("inf")
        for player in self.world.players:
            if player.alive:
                dst = player.position.get_dist_sqrd((x, y))
                if dst < min_dst:
                    closest = player
                    min_dst = dst
        return closest

    def spawn_enemies(
        self, count: int, character_type: CharacterType, center_x: int, center_y: int
    ):
        r = 1 + int(log2(count))  # randomize where group is centered
        for _ in range(count):
            x = center_x + random.randint(-r, r)
            y = center_y + random.randint(-r, r)
            yield self.spawn_enemy(character_type, x, y)

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

    async def publish(self, message: Message, **kwargs) -> None:
        await self.world.publish(message, **kwargs)

    def character_removed(self, character: Character):
        if isinstance(character, Enemy):
            self.enemies.remove(character)
