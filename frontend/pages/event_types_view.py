# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from datetime import datetime
import pytz

from .generals import theme
import requests
import pandas as pd
import json

import os

router = APIRouter(prefix='/event_types')
api_base_url = os.environ.get('API_URL')

def get_event_types_data():
    url = f"{api_base_url}/event_types"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

@router.page('/')
def parameters_view():
    ui.page_title("3CX CDR Server app - Event Types")    
    with theme.frame('- Event Types -'):
        ui.label('Event Types')
        event_types_data = get_event_types_data()
        grid_options= {
            'rowData': event_types_data,
            'columnDefs': [
                {'field': 'id', 'headerName': 'ID'},
                {'field': 'name', 'headerName': 'Name'},
                {'field': 'created_at', 'headerName': 'Created At'},
                {'field': 'updated_at', 'headerName': 'Updated At'}
            ],
            'defaultColDef': {
                        'flex': 1,
                        'minWidth': 30,
                        'resizable': True,
                        'cellStyle': {'fontSize': '14px'},
                        },
                        'horizontalScroll': True,
                        'rowSelection': 'single',
                        "stopEditingWhenCellsLoseFocus": True,
        }
        ui.aggrid(grid_options, theme='dark').classes('w-full')