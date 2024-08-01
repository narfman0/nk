"""Server handler of socket. Translates websocket bytes to and from messages for backend."""

import asyncio
import logging

from betterproto import serialized_on_wire
from fastapi import WebSocket
from nk_shared.proto import Message, PlayerJoined, PlayerJoinResponse, PlayerLeft
from starlette.websockets import WebSocketDisconnect, WebSocketState

from nk.db import User
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
    if websocket.state != WebSocketState.DISCONNECTED:
        try:
            await websocket.send_bytes(bytes(message))
        except RuntimeError as runtime_error:
            if "'websocket.send', after sending 'websocket.close'" in str(
                runtime_error
            ):
                logger.warning("FIXME websocket.send after websocket.close")
            else:
                raise runtime_error
        except WebSocketDisconnect:
            # theres a race condition with the above check and sending.
            # let's throw these away.
            logger.debug("WebSocketDisconnect after all")


async def handle_messages(player: Player, msg: Message):
    """Socket-level handler for messages, mostly passing through to world"""
    if serialized_on_wire(msg.player_join_request):
        await handle_player_join_request(player)
    elif serialized_on_wire(msg.text_message):
        await broadcast(player, msg)
    elif serialized_on_wire(msg.character_attacked):
        world.handle_character_attacked(msg.character_attacked)
    elif serialized_on_wire(msg.character_updated):
        world.handle_character_updated(msg.character_updated)
        await broadcast(player, msg)
    logger.debug("Handled message: %s from %s", msg, player.uuid)


async def handle_player_join_request(player: Player):
    """A player has joined. Handle initialization."""
    world.spawn_player(player)
    logger.info("Join request success: %s", player.uuid)
    response = PlayerJoinResponse(
        uuid=player.uuid, x=player.position.x, y=player.position.y
    )
    await player.messages.put(Message(player_join_response=response))
    await broadcast(player, Message(player_joined=PlayerJoined(uuid=player.uuid)))


async def handle_connected(websocket: WebSocket, user: User):
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

    player = Player(user=user)
    player.uuid = str(user.id)
    logger.info("Player uuid set to %s", player.uuid)
    try:
        await handler()
    except WebSocketDisconnect:
        logger.info("Disconnected from %s", player)
    await broadcast(player, Message(player_left=PlayerLeft(uuid=str(player.uuid))))
    x, y = player.position.x, player.position.y  # pylint: disable=no-member
    await user.set({User.x: x, User.y: y})
    logger.info("Successfully saved player post-logout")
    world.get_players().remove(player)
