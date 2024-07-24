from dataclasses import dataclass
from queue import Queue
import uuid

from nk.proto import Message


@dataclass
class Player:
    uuid: uuid.UUID
    messages: Queue[Message]
