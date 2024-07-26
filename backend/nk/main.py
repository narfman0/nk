from fastapi import FastAPI, WebSocket

from nk.socket_handler import handle_connected
from nk.logging import initialize_logging

initialize_logging()
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await handle_connected(websocket)
