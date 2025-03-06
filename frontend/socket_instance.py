# -*- coding: UTF-8 -*-

import websockets
import os

api_base_url = os.environ.get('API_URL').replace('http', 'ws')

async def connect_websocket():
    async with websockets.connect(f"{api_base_url}/ws") as websocket:
        try:
            while True:
                message = await websocket.recv()
                print(f"Received: {message}")
        except websockets.ConnectionClosed:
            print("Connection closed")

async def send_message(message: str):
    async with websockets.connect(f"{api_base_url}/ws") as websocket:
        await websocket.send(message)
