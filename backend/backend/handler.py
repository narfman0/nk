import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerJoined, PlayerLeft
from backend.models import Player

logger = logging.getLogger(__name__)
players: list[Player] = []


async def handle_connected(websocket: WebSocket, player: Player):
    def broadcast(message: Message):
        for remote_player in players:
            if not player == remote_player:
                remote_player.messages.put(message)

    try:
        while True:
            while not player.messages.empty():
                message = player.messages.get()
                logger.debug(f"Sending message {message} to {player.uuid}")
                await websocket.send_bytes(bytes(message))
            data = await websocket.receive_bytes()
            msg = Message().parse(data)
            if msg.player_join_request._serialized_on_wire:
                player.uuid = msg.player_join_request.uuid
                players.append(player)
                logger.info(f"Player join request success: {player.uuid}")
                broadcast(Message(player_joined=PlayerJoined(uuid=player.uuid)))
            elif msg.text_message._serialized_on_wire:
                broadcast(msg)
            elif msg.player_update._serialized_on_wire:
                broadcast(msg)
            logger.debug(f"Handled message: {msg} from {player.uuid}")
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
        broadcast(Message(player_left=PlayerLeft(uuid=player.uuid)))
        players.remove(player)
