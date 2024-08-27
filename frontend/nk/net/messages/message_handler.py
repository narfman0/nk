from abc import ABC

from nk_shared.proto import Message


class MessageHandler(ABC):  # pylint: disable=too-few-public-methods
    def handle_message(self, message: Message) -> bool:
        raise NotImplementedError
