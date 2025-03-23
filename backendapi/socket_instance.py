# -*- coding: UTF-8 -*-
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

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
        except (WebSocketDisconnect, ConnectionClosed) as e:
            # Ces exceptions indiquent que la connexion est fermée
            print(f"Connexion fermée: {e}")
            active_connections.discard(connection)
        except Exception as e:
            # Pour toute autre erreur inattendue
            print(f"Erreur inattendue: {e}")
            active_connections.discard(connection)