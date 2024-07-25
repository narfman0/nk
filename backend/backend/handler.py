import asyncio
import logging

from fastapi import WebSocket

from nk.proto import Message, PlayerJoined
from backend.models import Player

logger = logging.getLogger(__name__)
players: list[Player] = []


async def handle_connected(websocket: WebSocket, player: Player):
    def broadcast(message: Message):
        for remote_player in players:
            if not player == remote_player:
                remote_player.messages.put(message)

    async def consumer(message: Message):
        if message.player_join_request._serialized_on_wire:
            player.uuid = message.player_join_request.uuid
            players.append(player)
            logger.info(f"Player join request success: {player.uuid}")
            broadcast(Message(player_joined=PlayerJoined(uuid=player.uuid)))
        elif message.text_message._serialized_on_wire:
            broadcast(message)
        elif message.player_update._serialized_on_wire:
            broadcast(message)
        logger.debug(f"Handled message: {message} from {player.uuid}")

    async def consumer_handler(websocket: WebSocket):
        async for message in websocket:
            await consumer(Message().parse(message))

    async def producer_handler(websocket: WebSocket):
        while True:
            if not player.messages.empty():
                message = player.messages.get()
                logger.debug(f"Sending message {message} to {player.uuid}")
                await websocket.send_bytes(bytes(message))

    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
