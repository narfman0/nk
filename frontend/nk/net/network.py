import asyncio
import logging
from typing import Optional
from websockets.client import connect as wsaconnect, WebSocketClientProtocol
from websockets.sync.client import connect as ws_connect
import os
from queue import Queue

from os import environ
from threading import Thread

from nk.proto import Message

LOGGER = logging.getLogger(__name__)
USE_WSAPP = False
host = environ.get("WEBSOCKET_HOST", "localhost")
port = environ.get("WEBSOCKET_PORT", "7666")
url = f"ws://{host}:{port}/ws"


async def network_async_runner(received: Queue[Message], to_send: Queue[Message]):
    async with wsaconnect(url) as websocket:

        async def consumer_handler(websocket: WebSocketClientProtocol):
            async for message in websocket:
                received.put(Message().parse(message))

        async def producer_handler(websocket: WebSocketClientProtocol):
            while True:
                if not to_send.empty():
                    await websocket.send(bytes(to_send.get()))

        async def handler(websocket):
            consumer_task = asyncio.create_task(consumer_handler(websocket))
            producer_task = asyncio.create_task(producer_handler(websocket))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        await handler(websocket)


def network_async(received: Queue[Message], to_send: Queue[Message]):
    asyncio.run(network_async_runner(received, to_send))


def network_sync(received: Queue[Message], to_send: Queue[Message]):
    try:
        ws = ws_connect(url)
    except TimeoutError:
        LOGGER.error(f"Timed out connected to {url}")
        os._exit(1)
    while True:
        while not to_send.empty():
            message = to_send.get()
            ws.send(bytes(message))
        try:
            while True:
                data = ws.recv(timeout=0.001)
                received.put(Message().parse(data))
        except TimeoutError:
            pass  # expected
        except:
            os._exit(1)


class Network:

    def __init__(self):
        self._received_messages: Queue[Message] = Queue()
        self._to_send: Queue[Message] = Queue()
        self.network_thread = Thread(
            target=network_sync,
            name="network thread",
            args=(self._received_messages, self._to_send),
            daemon=True,
        )
        self.network_thread.start()

    def send(self, message: Message):
        self._to_send.put(message)

    def has_messages(self) -> bool:
        return not self._received_messages.empty()

    def next(self) -> Optional[Message]:
        if self.has_messages():
            return self._received_messages.get()
