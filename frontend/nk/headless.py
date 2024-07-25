import logging
import time
from uuid import uuid4
from math import sin, cos

from nk.net.network import Network
from nk.proto import Message, PlayerJoinRequest, PlayerUpdate
from nk.util.logging import initialize_logging

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


def get_start_pos(network: Network) -> tuple[float, float]:
    while True:
        while network.has_messages():
            message = network.next()
            if message.player_join_response._serialized_on_wire:
                if not message.player_join_response.success:
                    logger.info(f"Player join request failed")
                return (message.player_join_response.x, message.player_join_response.y)
        time.sleep(0.1)


def main():
    uuid = uuid4()
    network = Network()
    network.send(Message(player_join_request=PlayerJoinRequest(uuid=str(uuid))))
    i = 0
    center_x, center_y = get_start_pos(network)
    x, y = center_x, center_y
    next_update_time = 0.0
    while True:
        if next_update_time < time.time():
            next_update_time = time.time() + UPDATE_FREQUENCY
            x = center_x + sin(i / 5) * 2
            y = center_y + cos(i / 5) * 2
            i += UPDATE_FREQUENCY
            network.send(Message(player_update=PlayerUpdate(uuid=str(uuid), x=x, y=y)))
            logger.info(f"Sent: {(x,y)}")
        while network.has_messages():
            logger.info(f"Received: {network.next()}")
        network.send(Message())  # workaround for stimulating msg reception
        time.sleep(0.1)


if __name__ == "__main__":
    initialize_logging()
    main()
