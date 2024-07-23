import websocket

from nk.proto import message_pb2

ws = websocket.WebSocket()
ws.connect("ws://localhost:7666/ws")
for i in range(10):
    msg = message_pb2.Message()
    msg.text = f"Hello, Server {i}"
    result = ws.send_bytes(msg.SerializeToString())
    msg = message_pb2.Message()
    msg.ParseFromString(ws.recv())
    print(msg.text)
ws.close()
