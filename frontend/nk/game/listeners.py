from abc import ABC

from nk_shared.models.character import Character


class WorldListener(ABC):
    def character_added(self, character: Character):
        pass

    def character_removed(self, character: Character):
        pass
