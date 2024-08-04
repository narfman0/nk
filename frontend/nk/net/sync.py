import os
from queue import Queue

from loguru import logger
from nk_shared.proto import Message
from websockets.sync.client import connect


def handle_websocket(
    url: str, received: Queue[Message], to_send: Queue[Message], access_token: str
):
    headers = [("Authorization", f"Bearer {access_token}")]
    try:
        ws = connect(url, additional_headers=headers)
    except TimeoutError:
        logger.error("Timed out connected to {}", url)
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
        except:  # pylint: disable=bare-except
            os._exit(1)
