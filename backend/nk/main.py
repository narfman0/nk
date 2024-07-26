import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, WebSocket
from pygame.time import Clock

from nk.socket_handler import handle_connected
from nk.logging import initialize_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def world_updater():
        from nk.world import world

        clock = Clock()
        while True:
            dt = clock.tick(60) / 1000.0
            world.update(dt)
            await asyncio.sleep(max(0.01, 0.016 - dt))

    asyncio.gather(world_updater())
    yield


initialize_logging()
app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await handle_connected(websocket)
