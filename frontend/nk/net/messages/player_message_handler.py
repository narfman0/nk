from betterproto import serialized_on_wire
from loguru import logger
from nk_shared.proto import Message

from nk.game.world import World
from nk.net.messages.message_handler import MessageHandler


class PlayerMessageHandler(MessageHandler):
    def __init__(self, world: World):
        self.world = world

    def handle_message(self, message: Message) -> bool:
        if serialized_on_wire(message.player_respawned):
            self.handle_player_respawned(message)
        else:
            return False
        return True

    def handle_player_respawned(self, message: Message):
        details = message.player_respawned
        character = self.world.get_character_by_uuid(details.uuid)
        logger.info("Player respawned: {}", details)
        if character:
            character.hp = character.hp_max
            character.position = (details.x, details.y)
        else:
            logger.warning(
                "character_damaged no character found with uuid {}", details.uuid
            )
