from asyncio import Queue
from dataclasses import dataclass
import uuid

from nk.proto import Message


@dataclass
class Character:
    uuid: uuid.UUID
    messages: Queue[Message]
