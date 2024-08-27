from typing import Callable

from betterproto import serialized_on_wire
from nk_shared.proto import Message


class PlayerJoinResponseHandler:
    def __init__(self, callback: Callable):
        self.callback = callback

    def handle_message(self, message: Message) -> bool:
        if serialized_on_wire(message.player_join_response):
            self.callback(message)
