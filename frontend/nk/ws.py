import websocket

from nk.proto.message import Message

ws = websocket.WebSocket()
ws.connect("ws://localhost:7666/ws")
for i in range(10):
    msg = Message(text=f"Hello, Server {i}")
    result = ws.send_bytes(bytes(msg))
    msg = Message().parse(ws.recv())
    print(msg.text)
ws.close()
