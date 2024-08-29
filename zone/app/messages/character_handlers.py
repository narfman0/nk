from betterproto import serialized_on_wire
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

from app.messages.models import BaseMessageHandler
from app.models import WorldInterface


class UnknownCharacterError(Exception):
    pass


class CharacterMessageHandler(BaseMessageHandler):
    def __init__(self, world: WorldInterface):
        self.world = world

    async def handle_message(self, msg: Message) -> bool:
        if serialized_on_wire(msg.character_attacked):
            handle_character_attacked(self.world, msg.character_attacked)
        elif serialized_on_wire(msg.character_updated):
            await handle_character_updated(self.world, msg.character_updated)
        elif serialized_on_wire(msg.character_position_updated):
            await handle_character_position_updated(
                self.world, msg.character_position_updated
            )
        elif serialized_on_wire(msg.character_reloaded):
            await handle_character_reloaded(self.world, msg.character_reloaded)
        elif serialized_on_wire(msg.character_direction_updated):
            await handle_character_direction_updated(
                self.world, msg.character_direction_updated
            )
        else:
            return False
        return True


def handle_character_attacked(world: WorldInterface, details: CharacterAttacked):
    """Call character attack, does nothing if character does not exist"""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.attack(details.direction)


async def handle_character_position_updated(
    world: WorldInterface, details: CharacterPositionUpdated
):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.position = (details.x, details.y)
    character.velocity = (details.dx, details.dy)
    await world.publish(Message(origin_uuid=character.uuid, character_updated=details))


async def handle_character_reloaded(world: WorldInterface, details: CharacterReloaded):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.reload()
    await world.publish(Message(origin_uuid=character.uuid, character_reloaded=details))


async def handle_character_direction_updated(
    world: WorldInterface, details: CharacterDirectionUpdated
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


async def handle_character_updated(world: WorldInterface, details: CharacterUpdated):
    """Apply message details to relevant character. If character
    does not exist, do not do anything."""
    character = world.get_character_by_uuid(details.uuid)
    if not character:
        logger.warning("No character maching uuid: {}", details.uuid)
        return
    character.position = (details.x, details.y)
    character.velocity = (details.dx, details.dy)
    character.moving_direction = Direction(details.moving_direction)
    character.facing_direction = Direction(details.facing_direction)
    await world.publish(Message(origin_uuid=character.uuid, character_updated=details))
