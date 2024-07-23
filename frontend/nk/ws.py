import websocket

ws = websocket.WebSocket()

ws.connect("ws://localhost:8000/ws")
result = ws.send("Hello, Server")
print(result)
received = ws.recv()
ws.close()
print(received)
