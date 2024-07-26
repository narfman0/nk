import asyncio
import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.models import Player
from nk.proto import Message, PlayerLeft, PlayerJoined, PlayerJoinResponse
from nk.world import players

logger = logging.getLogger(__name__)


async def broadcast(origin: Player, message: Message):
    for remote_player in players:
        if not origin == remote_player:
            await remote_player.messages.put(message)


async def send_messages(player: Player, websocket: WebSocket):
    message = await player.messages.get()
    logger.debug(f"Sending message {message} to {player.uuid}")
    await websocket.send_bytes(bytes(message))


async def handle_messages(player: Player, msg: Message):
    if msg.player_join_request._serialized_on_wire:
        await handle_player_join_request(player, msg)
    elif msg.text_message._serialized_on_wire:
        await broadcast(player, msg)
    elif msg.player_update._serialized_on_wire:
        await broadcast(player, msg)
    logger.debug(f"Handled message: {msg} from {player.uuid}")


async def handle_player_join_request(player: Player, msg: Message):
    player.uuid = msg.player_join_request.uuid
    players.append(player)
    logger.info(f"Player join request success: {player.uuid}")
    response = PlayerJoinResponse(success=True, x=17, y=27)
    await player.messages.put(Message(player_join_response=response))
    await broadcast(player, Message(player_joined=PlayerJoined(uuid=player.uuid)))


async def handle_connected(websocket: WebSocket, player: Player):
    async def consumer():
        async for data in websocket.iter_bytes():
            await handle_messages(player, Message().parse(data))

    async def producer():
        while True:
            await send_messages(player, websocket)

    async def handler():
        consumer_task = asyncio.create_task(consumer())
        producer_task = asyncio.create_task(producer())
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    try:
        await handler()
    except WebSocketDisconnect:
        logger.info(f"Disconnected from {player}")
        broadcast(player, Message(player_left=PlayerLeft(uuid=player.uuid)))
        players.remove(player)
