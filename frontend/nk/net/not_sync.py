import asyncio
import logging
from websockets.client import connect
from queue import Queue

from nk.proto import Message

LOGGER = logging.getLogger(__name__)
USE_WSAPP = False


async def network_async_runner(
    url: str, received: Queue[Message], to_send: Queue[Message]
):
    async with connect(url) as websocket:

        async def consumer_handler():
            async for message in websocket:
                received.put(Message().parse(message))

        async def producer_handler():
            while True:
                if not to_send.empty():
                    await websocket.send(bytes(to_send.get()))

        async def handler():
            consumer_task = asyncio.create_task(consumer_handler())
            producer_task = asyncio.create_task(producer_handler())
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        await handler()


def handle_websocket(url: str, received: Queue[Message], to_send: Queue[Message]):
    asyncio.run(network_async_runner(url, received, to_send))
