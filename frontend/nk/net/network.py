import logging
from typing import Optional
from websockets.sync.client import connect as ws_connect
import os

from os import environ
from queue import Queue
from threading import Thread

from nk.proto import Message

LOGGER = logging.getLogger(__name__)
USE_WSAPP = False


def network_run(received: Queue[Message], to_send: Queue[Message]):
    host = environ.get("WEBSOCKET_HOST", "localhost")
    port = environ.get("WEBSOCKET_PORT", "7666")
    url = f"ws://{host}:{port}/ws"
    ws = ws_connect(url)

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
            target=network_run,
            name="network thread",
            args=(self._received_messages, self._to_send),
        ).start()

    def send(self, message: Message):
        self._to_send.put(message)

    def has_messages(self) -> bool:
        return not self._received_messages.empty()

    def next(self) -> Optional[Message]:
        if self.has_messages():
            return self._received_messages.get()
