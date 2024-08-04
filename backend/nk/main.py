import asyncio
import logging
from contextlib import asynccontextmanager
from os import environ

from beanie import init_beanie
from fastapi import FastAPI, WebSocket
import httpx
from nk_shared.util.logging import initialize_logging
from pygame.time import Clock

from nk.db import Character, db
from nk.socket_handler import handle_connected
from nk.world import world

logger = logging.getLogger(__name__)
AUTH_BASE_URL = environ.get("AUTH_BASE_URL", "https://auth")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """App-level startup and teardown method. We need to tick world regularly,
    and this is how we do it with the current implementation."""

    await init_beanie(
        database=db,
        document_models=[
            Character,
        ],
    )

    async def world_updater():
        clock = Clock()
        while True:
            dt = clock.tick(60) / 1000.0
            world.update(dt)
            try:
                await asyncio.sleep(max(0.01, 0.016 - dt))
            except asyncio.CancelledError:
                logger.warning("World update loop sleep cancelled, killing")
                break

    asyncio.gather(world_updater())
    yield


initialize_logging()
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Client entrypoint to game server"""
    await websocket.accept()
    response = httpx.get(
        AUTH_BASE_URL + "/users/me",
        headers={"Authorization": websocket.headers["Authorization"]},
    )
    if not response.is_success:
        logger.warning("Auth request failed %s", response)
    user_id = response.json()["user"]
    logger.info("Client logged in as %s", user_id)
    await handle_connected(websocket, user_id)
