import websocket

from nk.proto.message import Message, TextMessage

ws = websocket.WebSocket()
ws.connect("ws://localhost:7666/ws")
for i in range(10):
    text_message = TextMessage(text=f"Hello, Server {i}")
    result = ws.send_bytes(bytes(Message(text_message=text_message)))
    response = Message().parse(ws.recv())
    if response.text_message:
        print(response.text_message.text)
ws.close()
