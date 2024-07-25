import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerLeft, PlayerJoined, PlayerJoinResponse
from backend.models import Player
from backend.world import players

logger = logging.getLogger(__name__)


def broadcast(origin: Player, message: Message):
    for remote_player in players:
        if not origin == remote_player:
            remote_player.messages.put(message)


async def send_messages(player: Player, websocket: WebSocket):
    while not player.messages.empty():
        message = player.messages.get()
        logger.debug(f"Sending message {message} to {player.uuid}")
        await websocket.send_bytes(bytes(message))


def receive_messages(player: Player, msg: Message):
    if msg.player_join_request._serialized_on_wire:
        handle_player_join_request(player, msg)
    elif msg.text_message._serialized_on_wire:
        broadcast(player, msg)
    elif msg.player_update._serialized_on_wire:
        broadcast(player, msg)
    logger.debug(f"Handled message: {msg} from {player.uuid}")


def handle_player_join_request(player: Player, msg: Message):
    player.uuid = msg.player_join_request.uuid
    players.append(player)
    logger.info(f"Player join request success: {player.uuid}")
    response = PlayerJoinResponse(success=True, x=17, y=27)
    player.messages.put(Message(player_join_response=response))
    broadcast(player, Message(player_joined=PlayerJoined(uuid=player.uuid)))


async def handle_connected(websocket: WebSocket, player: Player):
    try:
        while True:
            await send_messages(player, websocket)
            data = await websocket.receive_bytes()
            receive_messages(player, Message().parse(data))
    except WebSocketDisconnect:
        logger.info(f"Disconnected from {player}")
        broadcast(player, Message(player_left=PlayerLeft(uuid=player.uuid)))
        players.remove(player)
