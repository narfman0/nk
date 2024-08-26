from betterproto import serialized_on_wire
from nk_shared.proto import Message

from app.messages import character_handlers, player_handlers
from app.models import WorldComponentProvider


class MessageHandler:  # pylint: disable=too-few-public-methods
    def __init__(self, world: WorldComponentProvider):
        self.world = world

    async def handle_message(self, msg: Message):
        if serialized_on_wire(msg.character_attacked):
            character_handlers.handle_character_attacked(
                self.world, msg.character_attacked
            )
        elif serialized_on_wire(msg.character_updated):
            await character_handlers.handle_character_updated(
                self.world, msg.character_updated
            )
        elif serialized_on_wire(msg.character_position_updated):
            await character_handlers.handle_character_position_updated(
                self.world, msg.character_position_updated
            )
        elif serialized_on_wire(msg.character_reloaded):
            await character_handlers.handle_character_reloaded(
                self.world, msg.character_reloaded
            )
        elif serialized_on_wire(msg.character_direction_updated):
            await character_handlers.handle_character_direction_updated(
                self.world, msg.character_direction_updated
            )
        elif serialized_on_wire(msg.player_connected):
            await player_handlers.handle_player_connected(
                self.world, msg.player_connected
            )
        elif serialized_on_wire(msg.player_disconnected):
            await player_handlers.handle_player_disconnected(
                self.world, msg.player_disconnected
            )
        elif serialized_on_wire(msg.text_message):
            await self.world.publish(msg)
