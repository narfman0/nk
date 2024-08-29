from nk_shared.proto import Message

from app.ai.ai import Ai
from app.messages.character_handlers import CharacterMessageHandler
from app.messages.models import BaseMessageHandler
from app.messages.player_handlers import PlayerMessageHandler
from app.messages.util_handlers import UtilMessageHandler
from app.models import WorldInterface


class MessageHandler:
    def __init__(self, world: WorldInterface, ai: Ai):
        self.handlers: list[BaseMessageHandler] = [
            CharacterMessageHandler(world),
            PlayerMessageHandler(world),
            UtilMessageHandler(world, ai),
        ]

    async def handle_message(self, msg: Message):
        for handler in self.handlers:
            if await handler.handle_message(msg):
                return
