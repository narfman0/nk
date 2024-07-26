import logging
from nk.world.models import Character

logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players: list[Character] = []

    def get_players(self) -> list[Character]:
        return self.players
