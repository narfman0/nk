from betterproto import serialized_on_wire
from nk_shared.proto import Message

from app.messages import character_handlers, player_handlers, util_handlers
from app.models import AiProtocol, WorldComponentProvider


class MessageHandler:
    def __init__(self, world: WorldComponentProvider, ai: AiProtocol):
        self.world = world
        self.ai = ai

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
            await util_handlers.handle_text_message(self.world, msg.text_message)
        elif serialized_on_wire(msg.spawn_requested):
            await util_handlers.handle_spawn_requested(
                self.world, self.ai, msg.spawn_requested
            )
