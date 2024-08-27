import random
import time
from math import cos, sin

from betterproto import serialized_on_wire
from loguru import logger
from nk_shared.proto import CharacterType, CharacterUpdated, Message

from nk.net import Network
from nk.net.network import LoginException

UPDATE_FREQUENCY = 0.1


class Headless:

    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.uuid = None
        self.character_type = CharacterType.CHARACTER_TYPE_PIGSASSIN
        self.network = Network()
        self.i = 0
        self.next_update_time = 0.0

    def connect(self):
        email = f"headless-{random.randint(1,999)}@blastedstudios.com"
        try:
            self.network.register(email=email, password="password")
        except LoginException as e:
            if "EXISTS" not in str(e):
                raise e
        token = self.network.login(email=email, password="password")
        self.network.connect(token)
        self.handle_join_response()

    def update(self):
        if self.next_update_time < time.time():
            self.next_update_time = time.time() + UPDATE_FREQUENCY
            x = self.start_x + sin(self.i / 5) * 2
            y = self.start_y + cos(self.i / 5) * 2
            self.i += UPDATE_FREQUENCY
            self.network.send(
                Message(
                    character_updated=CharacterUpdated(
                        uuid=self.uuid,
                        x=x,
                        y=y,
                        character_type=self.character_type,
                    )
                )
            )
            logger.debug("Sent: ({},{})", x, y)
        while self.network.has_messages():
            self.network.next()

    def handle_join_response(self):
        while True:
            while self.network.has_messages():
                message = self.network.next()
                if serialized_on_wire(message.player_join_response):
                    details = message.player_join_response
                    if not details.uuid:
                        # pylint: disable-next=broad-exception-raised
                        raise Exception("Player join request failed")
                    self.start_x, self.start_y = details.x, details.y
                    self.uuid = details.uuid
                    logger.info(
                        "Joined as {} at {},{}", self.uuid, details.x, details.y
                    )
                    return
            time.sleep(0.1)


if __name__ == "__main__":
    headless = Headless()
    headless.connect()
    while True:
        headless.update()
        time.sleep(0.1)
