import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerLeft
from backend.models import Player
from backend.shared import receive_messages, send_messages, broadcast
from backend.world import players

logger = logging.getLogger(__name__)


async def handle_connected(websocket: WebSocket, player: Player):
    try:
        while True:
            await send_messages(player, websocket)
            data = await websocket.receive_bytes()
            receive_messages(player, Message().parse(data))
    except WebSocketDisconnect:
        logger.info(f"Received WebSocketDisconnect from {player}")
        broadcast(player, Message(player_left=PlayerLeft(uuid=player.uuid)))
        players.remove(player)
