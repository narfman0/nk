from loguru import logger
from nk_shared.proto import (
    CharacterAttacked,
    CharacterDirectionUpdated,
    CharacterPositionUpdated,
    CharacterReloaded,
    CharacterUpdated,
    Direction,
    Message,
)

from app.models import WorldComponentProvider


class UnknownCharacterError(Exception):
    pass


def handle_character_attacked(
    world: WorldComponentProvider, details: CharacterAttacked
):
    """Call character attack, does nothing if character does not exist"""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.attack(details.direction)


async def handle_character_position_updated(
    world: WorldComponentProvider, details: CharacterPositionUpdated
):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.body.position = (details.x, details.y)
    character.body.velocity = (details.dx, details.dy)
    await world.publish(Message(origin_uuid=character.uuid, character_updated=details))


async def handle_character_reloaded(
    world: WorldComponentProvider, details: CharacterReloaded
):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.reload()
    logger.info("Character reloading: {}", details.uuid)
    await world.publish(Message(origin_uuid=character.uuid, character_reloaded=details))


async def handle_character_direction_updated(
    world: WorldComponentProvider, details: CharacterDirectionUpdated
):
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.moving_direction = Direction(details.moving_direction)
    character.facing_direction = Direction(details.facing_direction)
    await world.publish(
        Message(origin_uuid=character.uuid, character_direction_updated=details)
    )


async def handle_character_updated(
    world: WorldComponentProvider, details: CharacterUpdated
):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.body.position = (details.x, details.y)
    character.body.velocity = (details.dx, details.dy)
    character.moving_direction = Direction(details.moving_direction)
    character.facing_direction = Direction(details.facing_direction)
    await world.publish(Message(origin_uuid=character.uuid, character_updated=details))
