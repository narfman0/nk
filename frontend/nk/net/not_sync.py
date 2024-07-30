import asyncio
import logging
from queue import Queue

from websockets import ConnectionClosed, WebSocketClientProtocol
from websockets.client import connect

from nk_shared.proto import Message

logger = logging.getLogger(__name__)


async def network_async_runner(
    url: str, received: Queue[Message], to_send: Queue[Message]
):
    async def consumer_handler(websocket: WebSocketClientProtocol):
        async for message in websocket:
            received.put(Message().parse(message))

    async def producer_handler(websocket: WebSocketClientProtocol):
        while True:
            if not to_send.empty():
                message = to_send.get()
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

    async for websocket in connect(url):
        try:
            await handler(websocket)
        except ConnectionClosed:
            logger.warning("Connection closed")


def handle_websocket(url: str, received: Queue[Message], to_send: Queue[Message]):
    asyncio.run(network_async_runner(url, received, to_send))
