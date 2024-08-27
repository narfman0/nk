from typing import Callable

from loguru import logger
from nk_shared.proto import CharacterType, Direction, Message
from pymunk import Vec2d

from nk.game.world import World


class CharacterMessageHandler:
    def __init__(self, world: World):
        self.world = world
        self.character_added_callback: Callable = None
        self.character_attacked_callback: Callable = None

    def handle_character_attacked(self, message: Message):
        details = message.character_attacked
        logger.info(details)
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.attack(details.direction)
            if self.character_attacked_callback:
                # pylint: disable-next=not-callable
                self.character_attacked_callback(character)
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
            character.body.position = Vec2d(details.x, details.y)
            character.body.velocity = Vec2d(details.dx, details.dy)
        else:
            logger.warning("No character found with uuid: {}", details.uuid)

    def handle_character_updated(self, message: Message):
        details = message.character_updated
        if self.world.player.uuid == details.uuid:
            logger.warning("Received character_updated for self")
            return
        character = self.world.get_character_by_uuid(details.uuid)
        if character:
            character.body.position = Vec2d(details.x, details.y)
            character.body.velocity = Vec2d(details.dx, details.dy)
        else:
            if details.character_type == CharacterType.CHARACTER_TYPE_PIGSASSIN:
                character = self.world.add_player(
                    uuid=details.uuid,
                    start_x=details.x,
                    start_y=details.y,
                )
            else:
                character = self.world.add_enemy(
                    uuid=details.uuid,
                    start_x=details.x,
                    start_y=details.y,
                    character_type=CharacterType(details.character_type),
                )
            if self.character_added_callback:
                self.character_added_callback(character)  # pylint: disable=not-callable
        character.facing_direction = Direction(details.facing_direction)
        character.moving_direction = Direction(details.moving_direction)
        character.hp = details.hp
