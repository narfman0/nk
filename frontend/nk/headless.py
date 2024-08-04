import logging
import random
import time
from math import cos, sin

from betterproto import serialized_on_wire
from nk.net.network import LoginException
from nk_shared.proto import (
    CharacterType,
    CharacterUpdated,
    Message,
    PlayerJoinRequest,
    PlayerJoinResponse,
)
from nk_shared.util.logging import initialize_logging

from nk.net import Network

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


def get_start_pos(network: Network) -> PlayerJoinResponse:
    while True:
        while network.has_messages():
            message = network.next()
            if serialized_on_wire(message.player_join_response):
                if not message.player_join_response.uuid:
                    # pylint: disable-next=broad-exception-raised
                    raise Exception("Player join request failed")
                return message.player_join_response
        time.sleep(0.1)


def main():
    email = f"headless-{random.randint(1,999)}@blastedstudios.com"
    character_type = CharacterType.CHARACTER_TYPE_PIGSASSIN
    logger.info("Starting headless session")
    network = Network()
    try:
        network.register(email=email, password="password")
    except LoginException as e:
        if "EXISTS" not in str(e):
            raise e
    token = network.login(email=email, password="password")
    network.connect(token)
    network.send(Message(player_join_request=PlayerJoinRequest(requested=True)))
    i = 0
    response = get_start_pos(network)
    x, y = response.x, response.y
    next_update_time = 0.0
    while True:
        if next_update_time < time.time():
            next_update_time = time.time() + UPDATE_FREQUENCY
            x = response.x + sin(i / 5) * 2
            y = response.y + cos(i / 5) * 2
            i += UPDATE_FREQUENCY
            network.send(
                Message(
                    character_updated=CharacterUpdated(
                        uuid=response.uuid,
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
