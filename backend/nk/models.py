from asyncio import Queue
from dataclasses import dataclass

from nk_shared.models import Character
from nk_shared.proto import Message


@dataclass
class Player(Character):
    messages: Queue[Message] = Queue()


@dataclass
class NPC(Character):
    center_x: int = None
    center_y: int = None
