from abc import ABC, abstractmethod
from asyncio import Queue
from dataclasses import dataclass, field
from typing import Protocol

import pymunk
from nk_shared.map import Map
from nk_shared.models import Character
from nk_shared.proto import CharacterType, Message


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


class WorldListener:
    def character_removed(self, character: Character):
        pass


class AiProtocol(Protocol):
    def spawn_enemy(
        self, character_type: CharacterType, center_x: int, center_y: int
    ) -> Enemy: ...


class WorldComponentProvider(ABC):
    @abstractmethod
    async def publish(self, message: Message, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_character_by_uuid(self, uuid: str) -> Character | None:
        raise NotImplementedError()

    @abstractmethod
    def add_listener(self, listener: WorldListener) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def enemies(self) -> list[Enemy]:
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
