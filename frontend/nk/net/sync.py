import logging
import os
from queue import Queue

from websockets.sync.client import connect

from nk_shared.proto import Message

logger = logging.getLogger(__name__)


def handle_websocket(url: str, received: Queue[Message], to_send: Queue[Message]):
    try:
        ws = connect(url)
    except TimeoutError:
        logger.error("Timed out connected to %s", url)
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
