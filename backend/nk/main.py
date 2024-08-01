import asyncio
import logging
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import Depends, FastAPI, WebSocket, WebSocketException
from nk_shared.util.logging import initialize_logging
from pygame.time import Clock

from nk.db import User, db
from nk.db.schemas import UserCreate, UserRead, UserUpdate
from nk.db.users import (
    UserManager,
    auth_backend,
    fastapi_users,
    get_jwt_strategy,
    get_user_manager,
)
from nk.socket_handler import handle_connected
from nk.world import world

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """App-level startup and teardown method. We need to tick world regularly,
    and this is how we do it with the current implementation."""

    await init_beanie(
        database=db,
        document_models=[
            User,
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

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, user_manager: UserManager = Depends(get_user_manager)
):
    """Client entrypoint to game server"""
    await websocket.accept()
    token = websocket.headers["Authorization"].removeprefix("Bearer ")
    user: User | None = await get_jwt_strategy().read_token(token, user_manager)
    if not user:
        raise WebSocketException(401, "Authorization failed")
    logger.info("Client logged in as %s", user.email)
    await handle_connected(websocket, user)
