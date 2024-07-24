import logging

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, PlayerJoined
from backend.logging import initialize_logging

logger = logging.getLogger(__name__)
app = FastAPI()
initialize_logging()
ws_to_player: dict[WebSocket, str] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def broadcast(message: Message):
        # TODO fixme
        for ws in ws_to_player.keys():
            if ws == websocket:  # skip current
                continue
            await ws.send_bytes(bytes(message))

    try:
        while True:
            data = await websocket.receive_bytes()
            msg = Message().parse(data)
            if msg.player_join_request._serialized_on_wire:
                uuid = msg.player_join_request.uuid
                ws_to_player[websocket] = uuid
                logger.info(f"Player join request success: {uuid}")
                broadcast(Message(player_joined=PlayerJoined(uuid=uuid)))
            elif msg.text_message._serialized_on_wire:
                broadcast(msg)
            logger.info(f"Handled message: {msg} from {ws_to_player.get(websocket)}")
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
