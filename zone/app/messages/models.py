from abc import ABC

from betterproto import Message


class BaseMessageHandler(ABC):
    async def handle_message(self, msg: Message) -> bool:
        raise NotImplementedError
