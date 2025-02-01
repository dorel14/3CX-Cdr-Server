# -*- coding: UTF-8 -*-
from fastapi import WebSocket

active_connections: set[WebSocket] = set()

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"Client connected. Total connections: {len(active_connections)}")

async def disconnect(websocket: WebSocket):
    try:
        active_connections.remove(websocket)
    except KeyError:
        pass  # Connection already removed
    print(f"Client disconnected. Total connections: {len(active_connections)}")

async def broadcast_message(message: dict):
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            active_connections.discard(connection)