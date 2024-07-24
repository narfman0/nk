from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from nk.proto import Message, TextMessage

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            msg = Message().parse(data)
            if msg.text_message:
                text = f"Message text was: {msg.text_message.text}"
                text_message = TextMessage(text=text)
                await websocket.send_bytes(bytes(Message(text_message=text_message)))
    except WebSocketDisconnect:
        print("Received WebSocketDisconnect")
