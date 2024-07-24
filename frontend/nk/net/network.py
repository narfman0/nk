import logging
from typing import Optional
import websocket
from os import environ

from nk.proto import Message

LOGGER = logging.getLogger(__name__)


class Network:
    def __init__(self):
        self.ws = websocket.WebSocket()
        host = environ.get("WEBSOCKET_HOST", "localhost")
        port = environ.get("WEBSOCKET_PORT", "7666")
        self.ws.connect(f"ws://{host}:{port}/ws")

    def send(self, message: Message):
        self.ws.send_bytes(bytes(message))

    def recv(self) -> Optional[Message]:
        response = Message().parse(self.ws.recv())
        if response.text_message:
            LOGGER.warn(response.text_message.text)
        return response

    def close(self):
        self.ws.close()
