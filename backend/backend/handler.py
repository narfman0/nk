import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerJoined, PlayerLeft, PlayerJoinResponse
from backend.models import Player

logger = logging.getLogger(__name__)
players: list[Player] = []


def broadcast(origin: Player, message: Message):
    for remote_player in players:
        if not origin == remote_player:
            remote_player.messages.put(message)


async def handle_connected(websocket: WebSocket, player: Player):

    async def send_messages():
        while not player.messages.empty():
            message = player.messages.get()
            logger.debug(f"Sending message {message} to {player.uuid}")
            await websocket.send_bytes(bytes(message))

    async def receive_messages():
        data = await websocket.receive_bytes()
        msg = Message().parse(data)
        if msg.player_join_request._serialized_on_wire:
            await handle_player_join_request(msg)
        elif msg.text_message._serialized_on_wire:
            broadcast(player, msg)
        elif msg.player_update._serialized_on_wire:
            broadcast(player, msg)
        logger.debug(f"Handled message: {msg} from {player.uuid}")

    async def handle_player_join_request(msg: Message):
        player.uuid = msg.player_join_request.uuid
        players.append(player)
        logger.info(f"Player join request success: {player.uuid}")
        response = PlayerJoinResponse(success=True, x=17, y=27)
        player.messages.put(Message(player_join_response=response))
        broadcast(player, Message(player_joined=PlayerJoined(uuid=player.uuid)))

    try:
        while True:
            await send_messages()
            await receive_messages()
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
        broadcast(player, Message(player_left=PlayerLeft(uuid=player.uuid)))
        players.remove(player)
