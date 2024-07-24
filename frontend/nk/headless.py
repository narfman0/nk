import logging
import time
import uuid

from nk.net.network import Network
from nk.proto import Message, TextMessage, PlayerJoinRequest
from nk.util.logging import initialize_logging

logger = logging.getLogger(__name__)


def main():
    identifier = uuid.uuid4()
    network = Network()
    network.send(Message(player_join_request=PlayerJoinRequest(uuid=str(identifier))))
    i = 0
    while True:
        text = f"{identifier} message {i}"
        network.send(Message(text_message=TextMessage(text=text)))
        logger.info(f"Sent: {text}")
        while network.has_messages():
            logger.info(f"Received: {network.next()}")
        i += 1
        time.sleep(1)


if __name__ == "__main__":
    initialize_logging()
    main()
