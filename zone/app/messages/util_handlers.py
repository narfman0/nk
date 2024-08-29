from loguru import logger
from nk_shared import builders
from nk_shared.proto import CharacterType, Message, SpawnRequested, TextMessage

from app.models import AiProtocol, WorldComponentProvider


async def handle_text_message(world: WorldComponentProvider, details: TextMessage):
    await world.publish(Message(text_message=details))


async def handle_spawn_requested(
    world: WorldComponentProvider,
    ai: AiProtocol,
    details: SpawnRequested,
):
    logger.info("Handling spawn requested: {}", details)
    character_type = CharacterType(details.character_type)
    for _ in range(details.count):
        enemy = ai.spawn_enemy(character_type, details.x, details.y)
        await world.publish(builders.build_character_updated(enemy))
