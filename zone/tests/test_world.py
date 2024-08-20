from unittest.mock import AsyncMock

import pytest

from app.world import World


class TestWorld:
    @pytest.mark.asyncio
    async def test_trivial_update(self):
        world = World()
        world.broadcast = AsyncMock(return_value=None)
        await world.update(0.016)
