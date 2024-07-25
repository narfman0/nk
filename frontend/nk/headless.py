import logging
import time
import uuid
from math import sin, cos

from nk.net.network import Network
from nk.proto import Heartbeat, Message, PlayerJoinRequest, PlayerUpdate
from nk.util.logging import initialize_logging

UPDATE_FREQUENCY = 1.0
logger = logging.getLogger(__name__)


def main():
    identifier = uuid.uuid4()
    network = Network()
    network.send(Message(player_join_request=PlayerJoinRequest(uuid=str(identifier))))
    i = 0
    center_x, center_y = (17.0, 27.0)
    x, y = center_x, center_y
    next_update_time = 0.0
    while True:
        if next_update_time < time.time():
            next_update_time = time.time() + UPDATE_FREQUENCY
            x = center_x + sin(i / 50) * 2
            y = center_y + cos(i / 50) * 2
            network.send(
                Message(player_update=PlayerUpdate(uuid=str(identifier), x=x, y=y))
            )
            logger.info(f"Sent: {(x,y)}")
        network.send(Message(heartbeat=Heartbeat()))
        while network.has_messages():
            logger.info(f"Received: {network.next()}")
        i += 1
        time.sleep(0.1)


if __name__ == "__main__":
    initialize_logging()
    main()
