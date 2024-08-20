import asyncio

from beanie import init_beanie
from loguru import logger
from nk_shared.proto import Message
from pygame.time import Clock

from app.db import Character, db
from app.pubsub import subscribe
from app.world import World


async def updater(world: World):
    clock = Clock()
    while True:
        dt = clock.tick(60) / 1000.0
        await world.update(dt)
        try:
            await asyncio.sleep(max(0.01, 0.016 - dt))
        except asyncio.CancelledError:
            logger.warning("World update loop sleep cancelled, killing")
            break


async def consumer(world: World):
    channel = await subscribe()
    logger.info("Subscribed to channel successfully")
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            proto = Message().parse(message["data"])
            await world.handle_message(proto)


async def handler(world: World):
    consumer_task = asyncio.create_task(consumer(world))
    updater_task = asyncio.create_task(updater(world))
    _done, pending = await asyncio.wait(
        [consumer_task, updater_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


async def main():
    """App-level startup and teardown method. We need to tick world regularly,
    and this is how we do it with the current implementation."""
    await init_beanie(
        database=db,
        document_models=[
            Character,
        ],
    )
    await handler(World())


if __name__ == "__main__":
    asyncio.run(main())
