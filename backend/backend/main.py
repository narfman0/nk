import logging
from queue import Queue

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerJoined
from backend.logging import initialize_logging
from backend.models import Player

initialize_logging()
logger = logging.getLogger(__name__)
app = FastAPI()
players: list[Player] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = Player(uuid=None, messages=Queue())

    async def broadcast(message: Message):
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
                await broadcast(Message(player_joined=PlayerJoined(uuid=player.uuid)))
            elif msg.text_message._serialized_on_wire:
                await broadcast(msg)
            logger.debug(f"Handled message: {msg} from {player.uuid}")
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
        # TODO emit player left
        players.remove(player)
