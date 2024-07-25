import logging
from queue import Queue

from fastapi import FastAPI, WebSocket

from backend.logging import initialize_logging
from backend.models import Player
from backend.handler import handle_connected

initialize_logging()
logger = logging.getLogger(__name__)
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = Player(uuid=None, messages=Queue())
    await handle_connected(websocket, player)
    logger.info(f"Player disconnected: {player.uuid}")
