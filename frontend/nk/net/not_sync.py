import asyncio
from queue import Queue

from asyncio import Queue
from loguru import logger
from nk_shared.proto import Message
from websockets import ConnectionClosed, WebSocketClientProtocol
from websockets.client import connect


async def network_async_runner(
    url: str, received: Queue[Message], to_send: Queue[Message], access_token: str
):
    async def consumer_handler(websocket: WebSocketClientProtocol):
        async for message in websocket:
            await received.put(Message().parse(message))

    async def producer_handler(websocket: WebSocketClientProtocol):
        while True:
            message = await to_send.get()
            await websocket.send(bytes(message))

    async def handler(websocket: WebSocketClientProtocol):
        consumer_task = asyncio.create_task(consumer_handler(websocket))
        producer_task = asyncio.create_task(producer_handler(websocket))
        _done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    headers = [("Authorization", f"Bearer {access_token}")]
    drops = 0
    async for websocket in connect(url, extra_headers=headers):
        if drops >= 3:
            logger.error("Dropped too many connections, exiting")
            break
        try:
            await handler(websocket)
        except ConnectionClosed:
            logger.warning("Connection closed")
            drops += 1


def handle_websocket(
    url: str, received: Queue[Message], to_send: Queue[Message], access_token: str
):
    asyncio.run(network_async_runner(url, received, to_send, access_token))
