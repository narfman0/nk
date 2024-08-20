from os import environ

import httpx
from fastapi import FastAPI, WebSocket
from loguru import logger

from app.handler import handle_connected

AUTH_BASE_URL = environ.get("AUTH_BASE_URL", "http://auth:8080")


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Client entrypoint to game server"""
    await websocket.accept()
    response = httpx.get(
        AUTH_BASE_URL + "/users/me",
        headers={"Authorization": websocket.headers["Authorization"]},
    )
    if not response.is_success:
        logger.warning("Auth request failed {}", response)
    user_id = response.json()["id"]
    logger.info("Client logged in as {}", user_id)
    await handle_connected(websocket, user_id)
