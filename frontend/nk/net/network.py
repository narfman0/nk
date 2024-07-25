import logging
from typing import Optional
from queue import Queue

from os import environ
from threading import Thread

from nk.proto import Message
from nk.net.sync import handle_websocket

LOGGER = logging.getLogger(__name__)

host = environ.get("WEBSOCKET_HOST", "localhost")
port = environ.get("WEBSOCKET_PORT", "7666")
url = f"ws://{host}:{port}/ws"


class Network:

    def __init__(self):
        self._received_messages: Queue[Message] = Queue()
        self._to_send: Queue[Message] = Queue()
        self.network_thread = Thread(
            target=handle_websocket,
            name="network thread",
            args=(url, self._received_messages, self._to_send),
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
