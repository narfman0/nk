import os

import redis.asyncio as redis
from redis.client import PubSub

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost"))


async def subscribe() -> PubSub:
    pubsub = r.pubsub()
    await pubsub.subscribe("zone")
    return pubsub


async def publish(message: bytes, channel: str = "api") -> None:
    await r.publish(channel, message)
