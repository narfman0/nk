from asyncio import Queue
from dataclasses import dataclass, field

from nk_shared.models import Character
from nk_shared.proto import Message


@dataclass
class Player(Character):
    messages: Queue[Message] = field(default_factory=Queue)


@dataclass
class Enemy(Character):
    center_x: int = None
    center_y: int = None
