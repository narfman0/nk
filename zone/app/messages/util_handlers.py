from betterproto import serialized_on_wire
from loguru import logger
from nk_shared import builders
from nk_shared.proto import CharacterType, Message, SpawnRequested, TextMessage

from app.models import AiInterface, WorldInterface


class UtilHandler:
    def __init__(self, world: WorldInterface, ai: AiInterface):
        self.world = world
        self.ai = ai

    async def handle_message(self, msg: Message) -> bool:
        if serialized_on_wire(msg.text_message):
            await handle_text_message(self.world, msg.text_message)
        elif serialized_on_wire(msg.spawn_requested):
            await handle_spawn_requested(self.world, self.ai, msg.spawn_requested)
        else:
            return False
        return True


async def handle_text_message(world: WorldInterface, details: TextMessage):
    await world.publish(Message(text_message=details))


async def handle_spawn_requested(
    world: WorldInterface,
    ai: AiInterface,
    details: SpawnRequested,
):
    logger.info("Handling spawn requested: {}", details)
    character_type = CharacterType(details.character_type)
    for _ in range(details.count):
        enemy = ai.spawn_enemy(character_type, details.x, details.y)
        await world.publish(builders.build_character_updated(enemy))
