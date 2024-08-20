from abc import ABC, abstractmethod
from asyncio import Queue
from dataclasses import dataclass, field

import pymunk
from nk_shared.map import Map
from nk_shared.models import Character
from nk_shared.proto import Message


@dataclass
class Player(Character):
    """A remote player. Their websocket thread will tick and publish any messages to them."""

    messages: Queue[Message] = field(default_factory=Queue)
    user_id: str = None

    def __post_init__(self):
        super().__post_init__()
        self.uuid = self.user_id


@dataclass
class Enemy(Character):
    """AI controlled enemy"""

    center_x: int = None
    center_y: int = None


class WorldComponentProvider(ABC):
    @abstractmethod
    async def broadcast(self, message: Message, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_character_by_uuid(self, uuid: str) -> Character | None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def players(self) -> list[Player]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def map(self) -> Map:
        raise NotImplementedError()

    @property
    @abstractmethod
    def space(self) -> pymunk.Space:
        raise NotImplementedError()
