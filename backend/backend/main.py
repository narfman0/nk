from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from backend.proto.message import Message

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            msg = Message().parse(data)
            await websocket.send_bytes(
                bytes(Message(text=f"Message text was: {msg.text}"))
            )
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
