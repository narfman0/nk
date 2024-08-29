from nk_shared.proto import Message

from app.messages.models import BaseHandler
from app.models import AiInterface, WorldInterface
from app.messages.character_handlers import CharacterHandler
from app.messages.player_handlers import PlayerHandler
from app.messages.util_handlers import UtilHandler


class MessageHandler:
    def __init__(self, world: WorldInterface, ai: AiInterface):
        self.world = world
        self.ai = ai
        self.handlers: list[BaseHandler] = [
            CharacterHandler(world),
            PlayerHandler(world),
            UtilHandler(world, ai),
        ]

    async def handle_message(self, msg: Message):
        for handler in self.handlers:
            if await handler.handle_message(msg):
                return
