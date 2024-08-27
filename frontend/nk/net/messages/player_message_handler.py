from loguru import logger
from nk_shared.proto import Message
from pymunk import Vec2d

from nk.game.world import World


class PlayerMessageHandler:
    def __init__(self, world: World):
        self.world = world

    def handle_player_respawned(self, message: Message):
        details = message.player_respawned
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.hp = character.hp_max
            character.body.position = Vec2d(details.x, details.y)
        else:
            logger.warning(
                "character_damaged no character found with uuid {}", details.uuid
            )
