import asyncio
import logging
from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk_shared.proto import Message, PlayerLeft, PlayerJoined, PlayerJoinResponse
from nk.models import Player
from nk.world import world

logger = logging.getLogger(__name__)


async def broadcast(origin: Player | None, message: Message):
    for remote_player in world.get_players():
        if origin != remote_player:
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
    elif msg.character_attacked._serialized_on_wire:
        world.handle_character_attacked(msg.character_attacked)
    elif msg.character_updated._serialized_on_wire:
        world.handle_character_updated(msg.character_updated)
        await broadcast(player, msg)
    logger.debug(f"Handled message: {msg} from {player.uuid}")


async def handle_player_join_request(player: Player, msg: Message):
    player.uuid = UUID(msg.player_join_request.uuid)
    world.spawn_player(player)
    logger.info(f"Join request success: {player.uuid}")
    response = PlayerJoinResponse(
        success=True, x=player.position.x, y=player.position.y
    )
    await player.messages.put(Message(player_join_response=response))
    await broadcast(player, Message(player_joined=PlayerJoined(uuid=str(player.uuid))))


async def handle_connected(websocket: WebSocket):
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

    player = Player()
    try:
        await handler()
    except WebSocketDisconnect:
        logger.info(f"Disconnected from {player}")
    await broadcast(player, Message(player_left=PlayerLeft(uuid=str(player.uuid))))
    world.get_players().remove(player)
