# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator
from datetime import datetime
import pytz
from .generals import theme
import requests
import pandas as pd
import json
import websockets
import asyncio
import os

router = APIRouter(prefix='/parameters')
api_base_url = os.environ.get('API_URL')
# Add WebSocket event handler
async def handle_queue_websocket():
    uri = f"{api_base_url.replace('http', 'ws')}/ws"
    print(f"Attempting WebSocket connection to: {uri}")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("WebSocket connection established")
                while True:
                    message = await websocket.recv()
                    print(f"Received WebSocket message: {message}")
                    data = json.loads(message)
                    action = data.get('action')
                    if action == 'create':
                        print(f"Creating event with id: {data.get('event["id"]')}")
                        
                    elif action == 'update':
                        print(f"Updating event with id: {data.get('event["id"]')}")
                        
                    elif action == 'delete':
                        print(f"Deleting event with id: {data.get('event["id"]')}")
                        
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket error: {e}, attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)




@router.page('/')
def parameters_view():
    asyncio.create_task(handle_queue_websocket())
    ui.page_title("3CX CDR Server app - Parameters")    
    with theme.frame('- Parameters -'):
        ui.label('Parameters')