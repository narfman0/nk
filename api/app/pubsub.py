import os

import redis.asyncio as redis
from redis.client import PubSub

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost"))


async def subscribe(player_uuid: str) -> PubSub:
    pubsub = r.pubsub()
    await pubsub.subscribe("api", f"player-{player_uuid}")
    return pubsub


async def publish(message: bytes):
    await r.publish("zone", message)
