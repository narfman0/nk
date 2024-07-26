from asyncio import Queue

from fastapi import FastAPI, WebSocket

from nk.socket_handler import handle_connected
from nk.logging import initialize_logging
from nk.models import Player

initialize_logging()
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = Player(uuid=None, messages=Queue())
    await handle_connected(websocket, player)
