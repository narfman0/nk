import asyncio

import sentry_sdk
from beanie import init_beanie
from loguru import logger
from nk_shared.profiling import begin_profiling, end_profiling
from nk_shared.proto import Message
from pygame.time import Clock

from app.db import Character, db
from app.pubsub import subscribe
from app.settings import SENTRY_DSN
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


def init_sentry():
    if not SENTRY_DSN:
        logger.warning("SENTRY_DSN not set, skipping Sentry initialization")
        return
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )


async def main():
    """App-level startup and teardown method. We need to tick world regularly,
    and this is how we do it with the current implementation."""
    init_sentry()
    await init_beanie(
        database=db,
        document_models=[
            Character,
        ],
    )
    begin_profiling()
    try:
        await handler(World())
    except Exception as e:
        raise e
    finally:
        end_profiling()


if __name__ == "__main__":
    asyncio.run(main())
