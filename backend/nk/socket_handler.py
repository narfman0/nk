"""Server handler of socket. Translates websocket bytes to and from messages for backend."""

import asyncio
import contextlib
import logging

from betterproto import serialized_on_wire
from fastapi import Depends, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager
from starlette.websockets import WebSocketDisconnect

from nk_shared.proto import (
    Message,
    PlayerLeft,
    PlayerJoined,
    PlayerJoinResponse,
    PlayerLoginResponse,
)
from nk.db import db, get_user_db
from nk.users import UserManager, get_user_manager, fastapi_users
from nk.models import Player
from nk.world import world

logger = logging.getLogger(__name__)


async def broadcast(origin: Player | None, message: Message):
    """Put the message on the msg queue for every player who is not origin"""
    for remote_player in world.get_players():
        if origin != remote_player:
            await remote_player.messages.put(message)


async def send_messages(player: Player, websocket: WebSocket):
    """Push all messages on player's queue through their socket"""
    message = await player.messages.get()
    logger.debug("Sending message %s to %s", message, player.uuid)
    await websocket.send_bytes(bytes(message))


async def handle_messages(player: Player, msg: Message):
    """Socket-level handler for messages, mostly passing through to world"""
    if serialized_on_wire(msg.player_join_request):
        await handle_player_join_request(player, msg)
    elif serialized_on_wire(msg.player_login_request):
        await handle_player_login_request(player, msg)
    elif serialized_on_wire(msg.text_message):
        await broadcast(player, msg)
    elif serialized_on_wire(msg.character_attacked):
        world.handle_character_attacked(msg.character_attacked)
    elif serialized_on_wire(msg.character_updated):
        world.handle_character_updated(msg.character_updated)
        await broadcast(player, msg)
    logger.debug("Handled message: %s from %s", msg, player.uuid)


async def handle_player_login_request(
    player: Player,
    msg: Message,
):
    details = msg.player_login_request
    _credentials = OAuth2PasswordRequestForm(
        username=details.email,
        password=details.password,
    )
    # get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    # get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    # get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    # async with get_user_manager_context(db) as user_manager:
    #     user = await user_manager.authenticate(credentials)
    collection = db.get_collection("User")
    user = await collection.find_one(filter={"email": details.email})
    success = bool(user) and user["is_active"]
    logger.info(
        "User %s attempted login, success: %r",
        details.email,
        success,
    )
    await player.messages.put(
        Message(player_login_response=PlayerLoginResponse(success=success))
    )


async def handle_player_join_request(player: Player, msg: Message):
    """A player has joined. Handle initialization."""
    player.uuid = msg.player_join_request.uuid
    world.spawn_player(player)
    logger.info("Join request success: %s", player.uuid)
    response = PlayerJoinResponse(
        success=True, x=player.position.x, y=player.position.y
    )
    await player.messages.put(Message(player_join_response=response))
    await broadcast(player, Message(player_joined=PlayerJoined(uuid=str(player.uuid))))


async def handle_connected(websocket: WebSocket):
    """Handle the lifecycle of the websocket"""

    async def consumer():
        """Translate bytes on the wire to messages"""
        async for data in websocket.iter_bytes():
            await handle_messages(player, Message().parse(data))

    async def producer():
        """Emit queued messages to player"""
        while True:
            await send_messages(player, websocket)

    async def handler():
        """Socket lifecycle handler. Handles producing and consuming simultaneously."""
        consumer_task = asyncio.create_task(consumer())
        producer_task = asyncio.create_task(producer())
        _done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    player = Player()
    try:
        await handler()
    except WebSocketDisconnect:
        logger.info("Disconnected from %s", player)
    await broadcast(player, Message(player_left=PlayerLeft(uuid=str(player.uuid))))
    world.get_players().remove(player)
