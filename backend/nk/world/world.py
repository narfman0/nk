import logging
from nk.world.models import Player

logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players: list[Player] = []

    def get_players(self) -> list[Player]:
        return self.players
