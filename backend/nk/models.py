from asyncio import Queue
from dataclasses import dataclass, field

from nk_shared.models import Character
from nk_shared.proto import Message

from nk.db import User


@dataclass
class Player(Character):
    """A remote player. Their websocket thread will tick and publish any messages to them."""

    messages: Queue[Message] = field(default_factory=Queue)
    user: User = None


@dataclass
class Enemy(Character):
    """AI controlled enemy"""

    center_x: int = None
    center_y: int = None
