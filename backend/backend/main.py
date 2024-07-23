from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from backend.proto import message_pb2

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            msg = message_pb2.Message()
            msg.ParseFromString(data)
            msg.text = f"Message text was: {msg.text}"
            await websocket.send_bytes(msg.SerializeToString())
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
