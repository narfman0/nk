"""Server handler of socket. Translates websocket bytes to and from messages for backend."""

import asyncio

from fastapi import WebSocket
from loguru import logger
from nk_shared import builders
from nk_shared.proto import Message
from starlette.websockets import WebSocketDisconnect, WebSocketState

from nk.models import Player
from nk.world import world


async def send_messages(player: Player, websocket: WebSocket):
    """Push all messages on player's queue through their socket"""
    message = await player.messages.get()
    if websocket.state != WebSocketState.DISCONNECTED:
        try:
            await websocket.send_bytes(bytes(message))
        except RuntimeError as runtime_error:
            if "'websocket.send', after sending 'websocket.close'" in str(
                runtime_error
            ) or 'Cannot call "send" once a close message has been sent.' in str(
                runtime_error
            ):
                logger.warning("FIXME websocket.send after websocket.close")
            else:
                raise runtime_error
        except WebSocketDisconnect:
            # theres a race condition with the above check and sending.
            # let's throw these away.
            logger.debug("WebSocketDisconnect after all")


async def handle_connected(websocket: WebSocket, user_id: str):
    """Handle the lifecycle of the websocket"""

    async def consumer():
        """Translate bytes on the wire to messages"""
        async for data in websocket.iter_bytes():
            await world.handle_message(player, Message().parse(data))

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

    player = Player(user_id=user_id)
    try:
        await handler()
    except WebSocketDisconnect:
        logger.info("Disconnected from {}", player)
    await world.handle_message(player, builders.build_player_disconnected(player.uuid))
