import asyncio
import logging
from typing import Optional
from websockets.client import connect as wsaconnect, WebSocketClientProtocol
from websockets.sync.client import connect as ws_connect
import os

from os import environ
from collections import deque
from threading import Thread

from nk.proto import Message

LOGGER = logging.getLogger(__name__)
USE_WSAPP = False
host = environ.get("WEBSOCKET_HOST", "localhost")
port = environ.get("WEBSOCKET_PORT", "7666")
url = f"ws://{host}:{port}/ws"


def network_async(received: deque[Message], to_send: deque[Message]):
    async def process():
        async with wsaconnect(url) as websocket:

            async def read(websocket: WebSocketClientProtocol):
                async for message in websocket:
                    await received.append(Message().parse(message))

            async def write(websocket: WebSocketClientProtocol):
                while True:
                    if to_send:
                        await websocket.send(bytes(to_send.popleft()))

        await asyncio.gather(read(websocket), write(websocket))

    asyncio.run(process())


def network_sync(received: deque[Message], to_send: deque[Message]):
    ws = ws_connect(url)
    while True:
        while to_send:
            message = to_send.popleft()
            ws.send(bytes(message))
        try:
            while True:
                data = ws.recv(timeout=0.001)
                received.append(Message().parse(data))
        except TimeoutError:
            pass  # expected
        except:
            os._exit(1)


class Network:

    def __init__(self):
        self._received_messages: deque[Message] = deque()
        self._to_send: deque[Message] = deque()
        self.network_thread = Thread(
            target=network_sync,
            name="network thread",
            args=(self._received_messages, self._to_send),
            daemon=True,
        )
        self.network_thread.start()

    def send(self, message: Message):
        self._to_send.append(message)

    def has_messages(self) -> bool:
        return bool(self._received_messages)

    def next(self) -> Optional[Message]:
        return self._received_messages.popleft()
