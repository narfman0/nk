from typing import Protocol

from betterproto import serialized_on_wire
from loguru import logger
from nk_shared.models.character import Character
from nk_shared.proto import CharacterType, Direction, Message

from nk.game.world import World
from nk.net.messages.message_handler import MessageHandler


class CharacterMessageListener(Protocol):
    def character_attacked(self, character: Character): ...


class CharacterMessageHandler(MessageHandler):
    def __init__(self, world: World):
        self.world = world
        self.listeners: list[CharacterMessageListener] = []

    def handle_message(self, message: Message) -> bool:
        if serialized_on_wire(message.character_position_updated):
            self.handle_character_position_updated(message)
        if serialized_on_wire(message.character_direction_updated):
            self.handle_character_direction_updated(message)
        elif serialized_on_wire(message.character_updated):
            self.handle_character_updated(message)
        elif serialized_on_wire(message.character_attacked):
            self.handle_character_attacked(message)
        elif serialized_on_wire(message.character_damaged):
            self.handle_character_damaged(message)
        elif serialized_on_wire(message.character_reloaded):
            self.handle_character_reloaded(message)
        else:
            return False
        return True

    def handle_character_attacked(self, message: Message):
        details = message.character_attacked
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.attack(details.direction)
            for listener in self.listeners:
                listener.character_attacked(character)
        else:
            logger.warning(
                "character_attacked no character found with uuid {}", details.uuid
            )

    def handle_character_damaged(self, message: Message):
        details = message.character_damaged
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.handle_damage_received(details.damage)
            character.hp = details.hp
        else:
            logger.warning(
                "character_damaged no character found with uuid {}", details.uuid
            )

    def handle_character_reloaded(self, message: Message):
        details = message.character_reloaded
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.reload()
        else:
            logger.warning(
                "character_reloaded no character found with uuid {}", details.uuid
            )

    def handle_character_direction_updated(self, message: Message):
        details = message.character_direction_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.facing_direction = Direction(details.facing_direction)
            character.moving_direction = Direction(details.moving_direction)
        else:
            logger.warning("No character found with uuid: {}", details.uuid)

    def handle_character_position_updated(self, message: Message):
        details = message.character_position_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.position = (details.x, details.y)
            character.velocity = (details.dx, details.dy)
        else:
            logger.warning("No character found with uuid: {}", details.uuid)

    def handle_character_updated(self, message: Message):
        details = message.character_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.position = (details.x, details.y)
            character.velocity = (details.dx, details.dy)
        else:
            character = self.world.add_character(
                uuid=details.uuid,
                start_x=details.x,
                start_y=details.y,
                character_type=CharacterType(details.character_type),
            )
        character.facing_direction = Direction(details.facing_direction)
        character.moving_direction = Direction(details.moving_direction)
        character.hp = details.hp
