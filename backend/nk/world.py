import logging
import random
from math import sin, cos

from nk_shared.models import Character

from nk.models import Player
from nk.proto import Message, CharacterUpdate

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players: list[Player] = []
        self.enemies: list[Character] = []
        for _i in range(5):
            pos = (20 + random.randint(-3, 3), 27 + random.randint(-3, 3))
            enemy = Character(position=pos)
            enemy.temp_center = pos  # we'll remove this eventually
            self.enemies.append(enemy)
        self.i = 0.0
        self.next_update_time = 0.0

    def get_players(self) -> list[Player]:
        return self.players

    def update(self, dt: float):
        self.next_update_time -= dt
        if self.next_update_time <= 0:
            self.next_update_time = UPDATE_FREQUENCY
            self.i += UPDATE_FREQUENCY
            for enemy in self.enemies:
                x, y = enemy.temp_center
                x += sin(self.i / 5) * 2
                y += cos(self.i / 5) * 2
                enemy.body.position = (x, y)
                msg = Message(
                    character_update=CharacterUpdate(uuid=str(enemy.uuid), x=x, y=y)
                )
                for player in self.players:
                    player.messages.put_nowait(msg)


# Locally, this is the world directly. When deployed, this might be a handle to
# a message forwarder to the larger system.
world = World()
