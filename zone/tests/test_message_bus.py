from unittest.mock import AsyncMock, patch

import pytest
from nk_shared import builders
from nk_shared.proto import Direction, Message, TextMessage

from app.message_bus import MessageBus
from app.models import Player
from app.world import World


@pytest.fixture
def world() -> World:
    world = World()
    world.publish = AsyncMock(return_value=None)
    return world


@pytest.fixture
def message_bus(world: World) -> MessageBus:
    return MessageBus(world)


class TestMessageBus:

    @pytest.mark.asyncio
    async def test_handle_message_text(self, message_bus: MessageBus):
        msg = Message(text_message=TextMessage(text="test"))
        await message_bus.handle_message(msg)

    @pytest.mark.asyncio
    async def test_handle_character_updated(self, message_bus: MessageBus):
        player = Player(user_id="1234", moving_direction=Direction.DIRECTION_E)
        message_bus.world.players.append(player)
        msg = builders.build_character_updated(player)
        await message_bus.handle_message(msg)
