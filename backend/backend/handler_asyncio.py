import asyncio
import logging

from fastapi import WebSocket

from nk.proto import Message
from backend.models import Player
from backend.shared import receive_messages, send_messages

logger = logging.getLogger(__name__)


async def handle_connected(websocket: WebSocket, player: Player):
    async def consumer_handler():
        async for message in websocket:
            receive_messages(player, Message().parse(message))

    async def producer_handler():
        while True:
            await send_messages(player, websocket)

    async def handler():
        consumer_task = asyncio.create_task(consumer_handler())
        producer_task = asyncio.create_task(producer_handler())
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    await handler(websocket)
