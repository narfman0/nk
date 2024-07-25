from queue import Queue

from fastapi import FastAPI, WebSocket

from backend.socket_handler import handle_connected
from backend.logging import initialize_logging
from backend.models import Player

initialize_logging()
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = Player(uuid=None, messages=Queue())
    await handle_connected(websocket, player)
