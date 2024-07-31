from queue import Queue
import logging
from os import environ
from threading import Thread

import httpx

from nk_shared.proto import Message
from nk.net.sync import handle_websocket

host = environ.get("WEBSOCKET_HOST", "localhost")
port = environ.get("WEBSOCKET_PORT", "7666")
url = f"ws://{host}:{port}/ws"

logger = logging.getLogger(__name__)


class LoginException(Exception):
    pass


class Network:

    def __init__(self):
        self._received_messages: Queue[Message] = Queue()
        self._to_send: Queue[Message] = Queue()

    def connect(self, email: str, password: str):
        access_token = self.login(email, password)
        logger.info("Access token retrieved, connecting")
        network_thread = Thread(
            target=handle_websocket,
            name="network thread",
            args=(url, self._received_messages, self._to_send, access_token),
            daemon=True,
        )
        network_thread.start()

    def send(self, message: Message):
        self._to_send.put(message)

    def has_messages(self) -> bool:
        return not self._received_messages.empty()

    def next(self) -> Message | None:
        if self.has_messages():
            return self._received_messages.get()
        return None

    @classmethod
    def login(cls, email: str, password: str) -> str:
        response = httpx.post(
            f"http://{host}:{port}/auth/jwt/login",  # Change to your actual host and port
            data={"username": email, "password": password},
        )
        if response.status_code == 200:
            tokens = response.json()
            return tokens["access_token"]
        raise LoginException(f"Login failed: {response.text}")
