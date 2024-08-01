import logging
import time
from math import cos, sin

from betterproto import serialized_on_wire
from nk_shared.proto import CharacterType, CharacterUpdated, Message, PlayerJoinRequest
from nk_shared.util.logging import initialize_logging

from nk.net import Network

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


def get_start_pos(network: Network) -> tuple[float, float]:
    while True:
        while network.has_messages():
            message = network.next()
            if serialized_on_wire(message.player_join_response):
                if not message.player_join_response.success:
                    logger.info("Player join request failed")
                return (message.player_join_response.x, message.player_join_response.y)
        time.sleep(0.1)


def main():
    character_type = CharacterType.CHARACTER_TYPE_PIGSASSIN
    logger.info("Starting headless session")
    network = Network()
    network.send(Message(player_join_request=PlayerJoinRequest()))
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
            network.send(
                Message(
                    character_updated=CharacterUpdated(
                        uuid="TODOretrieveuuid",
                        x=x,
                        y=y,
                        character_type=character_type,
                    )
                )
            )
            logger.info("Sent: (%r,%r)}", x, y)
        while network.has_messages():
            msg = network.next()
            if serialized_on_wire(msg.character_attacked):
                logger.info("Received: %s", msg.character_attacked)
        time.sleep(0.1)


if __name__ == "__main__":
    initialize_logging()
    main()
