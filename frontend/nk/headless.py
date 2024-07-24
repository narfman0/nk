import time
import uuid

from nk.net.network import Network
from nk.proto import Message, TextMessage

identifier = uuid.uuid4()
i = 0
network = Network()
while True:
    network.send(Message(text_message=TextMessage(text=f"{identifier} message {i}")))
    i += 1
    time.sleep(1)
