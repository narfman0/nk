import logging

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, TextMessage
from backend.logging import initialize_logging

logger = logging.getLogger(__name__)
app = FastAPI()
initialize_logging()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            msg = Message().parse(data)
            if msg.text_message:
                text = f"Message text was: {msg.text_message.text}"
                logger.info(text)
                text_message = TextMessage(text=text)
                await websocket.send_bytes(bytes(Message(text_message=text_message)))
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
