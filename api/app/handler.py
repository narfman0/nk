"""Server handler of socket. Translates websocket bytes to and from messages for backend."""

import asyncio

from fastapi import WebSocket
from loguru import logger
from starlette.websockets import WebSocketDisconnect, WebSocketState

from app.proto import Message, PlayerConnected, PlayerDisconnected
from app.pubsub import publish, subscribe

logger.add("app.log")


async def send_messages(messages: asyncio.Queue[Message], websocket: WebSocket):
    """Push all messages on queue through their socket"""
    message = await messages.get()
    if websocket.state != WebSocketState.DISCONNECTED:
        try:
            await websocket.send_bytes(bytes(message))
        except RuntimeError as runtime_error:
            if "'websocket.send', after sending 'websocket.close'" in str(
                runtime_error
            ) or 'Cannot call "send" once a close message has been sent.' in str(
                runtime_error
            ):
                logger.warning("FIXME websocket.send after websocket.close")
            else:
                raise runtime_error
        except WebSocketDisconnect:
            # theres a race condition with the above check and sending.
            # let's throw these away.
            logger.debug("WebSocketDisconnect after all")


async def handle_connected(websocket: WebSocket, uuid: str):
    """Handle the lifecycle of the websocket"""

    async def consumer():
        """Translate bytes on the wire to messages"""
        async for data in websocket.iter_bytes():
            await publish(data)

    async def pubsub_consumer():
        channel = await subscribe(uuid)
        while True:
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                proto = Message().parse(message["data"])
                messages.put_nowait(proto)

    async def producer():
        """Emit queued messages"""
        while True:
            await send_messages(messages, websocket)

    async def handler():
        """Socket lifecycle handler. Handles producing and consuming simultaneously."""
        consumer_task = asyncio.create_task(consumer())
        pubsub_consumer_task = asyncio.create_task(pubsub_consumer())
        producer_task = asyncio.create_task(producer())
        _done, pending = await asyncio.wait(
            [consumer_task, pubsub_consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    messages = asyncio.Queue[Message]()
    await publish(bytes(Message(player_connected=PlayerConnected(uuid=uuid))))
    try:
        await handler()
    except WebSocketDisconnect:
        logger.info("Disconnected from {}", uuid)
    await publish(bytes(Message(player_disconnected=PlayerDisconnected(uuid=uuid))))
