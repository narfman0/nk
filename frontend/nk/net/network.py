from os import environ
from threading import Thread

from asyncio import Queue
import httpx
from loguru import logger
from nk_shared.proto import Message

from nk.net.not_sync import handle_websocket

AUTH_BASE_URL = environ.get("AUTH_BASE_URL", "http://localhost:8080")
HOST = environ.get("WEBSOCKET_HOST", "localhost")
PORT = environ.get("WEBSOCKET_PORT", "7666")
URL = f"ws://{HOST}:{PORT}/ws"


class LoginException(Exception):
    pass


class Network:

    def __init__(self):
        self._received_messages: Queue[Message] = Queue()
        self._to_send: Queue[Message] = Queue()

    def connect(self, access_token: str):
        network_thread = Thread(
            target=handle_websocket,
            name="network thread",
            args=(URL, self._received_messages, self._to_send, access_token),
            daemon=True,
        )
        network_thread.start()

    def send(self, message: Message):
        self._to_send.put_nowait(message)

    def has_messages(self) -> bool:
        return not self._received_messages.empty()

    def next(self) -> Message | None:
        if self.has_messages():
            return self._received_messages.get_nowait()
        return None

    @classmethod
    def register(cls, email: str, password: str):
        """Login to return a JWT"""
        response = httpx.post(
            f"{AUTH_BASE_URL}/auth/register",
            json={"email": email, "password": password},
        )
        if response.is_error:
            raise LoginException(f"Login failed: {response.text}")
        logger.info("Successfully registered user {}", email)

    @classmethod
    def login(cls, email: str, password: str) -> str:
        """Login to return a JWT"""
        response = httpx.post(
            f"{AUTH_BASE_URL}/auth/jwt/login",
            data={"username": email, "password": password},
        )
        if response.is_error:
            raise LoginException(f"Login failed: {response.text}")
        logger.info("Access token retrieved, connecting")
        return response.json()["access_token"]
