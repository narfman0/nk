import logging
import random
from math import sin, cos
from uuid import uuid4

from nk.world.models import Character, Player
from nk.proto import Message, CharacterUpdate

UPDATE_FREQUENCY = 0.1
logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players: list[Player] = []
        self.enemies: list[Character] = []
        for i in range(5):
            enemy = Character(uuid=uuid4())
            enemy.temp_center = (
                20 + random.randint(-3, 3),
                27 + random.randint(-3, 3),
            )  # we'll remove this eventually
            enemy.body.position = enemy.temp_center
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
