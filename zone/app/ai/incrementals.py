"""Inteligently update the network state of the enemy.
If we have not changed (much), skip the update."""

from nk_shared import builders
from nk_shared.proto import CharacterDirectionUpdated, CharacterPositionUpdated

from app.models import Enemy, WorldComponentProvider

REMOTE_UPDATE_THRESHOLD = 1

# represents a remote entity's perception of the enemy
enemy_remote_positions: dict[str, CharacterPositionUpdated] = {}
enemy_remote_directions: dict[str, CharacterDirectionUpdated] = {}


async def update_position(dt: float, world: WorldComponentProvider, enemy: Enemy):
    proto = builders.build_character_position_updated(enemy)
    enemy_remote = enemy_remote_positions.get(enemy.uuid)
    if enemy_remote:
        enemy_remote.x += enemy_remote.dx * dt
        enemy_remote.y += enemy_remote.dy * dt
        if (
            enemy.position.get_dist_sqrd((enemy_remote.x, enemy_remote.y))
            < REMOTE_UPDATE_THRESHOLD
            and enemy.body.velocity.get_dist_sqrd((enemy_remote.dx, enemy_remote.dy))
            < REMOTE_UPDATE_THRESHOLD
        ):
            return  # too similar to previous update, skip
    enemy_remote_positions[enemy.uuid] = proto.character_position_updated
    await world.publish(proto)


async def update_direction(world: WorldComponentProvider, enemy: Enemy):
    proto = builders.build_character_direction_updated(enemy)
    previous = enemy_remote_directions.get(enemy.uuid)
    if (
        previous is None
        or enemy.facing_direction != previous.facing_direction
        or enemy.moving_direction != previous.moving_direction
    ):
        enemy_remote_directions[enemy.uuid] = proto.character_direction_updated
        await world.publish(proto)
