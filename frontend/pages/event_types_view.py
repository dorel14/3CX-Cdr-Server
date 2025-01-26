# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter

from nicegui_tabulator import tabulator
from .generals import theme
import requests

import json

import os

router = APIRouter(prefix='/event_types')
api_base_url = os.environ.get('API_URL')

def get_event_types_data():
    url = f"{api_base_url}/v1/event_types"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

async def event_type_dialog(row_data=None):
    dialog = ui.dialog()
    data = {}

    if row_data:
        data = row_data
    else:
        data['name'] = ''

    with dialog, ui.card().classes('w-1/3'):
        ui.label('Event Type details')
        with ui.row().classes('flex-wrap'):
            name_input = ui.input(
                label='Name', 
                value=data.get('name', ''),
                on_change=lambda e: data.update({'name': e.value})
            )
            description_input = ui.input(
                label='Description',
                value=data.get('description', ''),
                on_change=lambda e: data.update({'description': e.value})
            )
            with ui.button(icon='palette'):
                picker = ui.color_picker(on_pick=lambda e: data.update({'color': e.color}))
                picker.q_color.props('default-view=palette no-header no-footer')

        async def handle_save():
            save_data = {
                'name': data.get('name'),
                'description': data.get('description'),
                'color': data.get('color')
            }
            
            if data.get('id'):
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.patch(
                    f"{api_base_url}/v1/event_types/{data['id']}", 
                    headers=headers,
                    data=json.dumps(save_data)
                )
            else:
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.post(
                    f"{api_base_url}/v1/event_types/",
                    headers=headers,
                    data=json.dumps(save_data)
                )
                
            if response.status_code == 200:
                ui.notify('Event Type saved successfully', type='positive')
                dialog.close()
                refresh_event_types.refresh()
            else:
                ui.notify(f'Operation failed: {response.status_code} {response.content}')
                
        with ui.row().classes('w-full justify-end'):
            ui.button('Save', on_click=handle_save).classes('text-xs')
            ui.button('Cancel', on_click=dialog.close).classes('text-xs')
    
    dialog.open()

@ui.refreshable
def refresh_event_types():
    event_types_data = get_event_types_data()
    tabulator({
        'data': event_types_data,
        'columns': [
            {'title': 'ID', 'field': 'id'},
            {'title': 'Name', 'field': 'name'},
            {'title': 'Description', 'field': 'description'},
            {'title': 'Color', 'field': 'color', 'formatter': 'color'},
            {'title': 'Date Added', 'field': 'date_added'},
            {'title': 'Date Modified', 'field': 'date_modified'},
        ],
        'height': 205,
    }).classes('w-full')

@router.page('/')
def event_types_page():
    ui.page_title("3CX CDR Server app - Event Types")
    with theme.frame('- Event Types -'):
        ui.label('Event Types')
    with ui.row().classes('w-full border-b pb-2'):
        ui.button('Add',
                icon='add',
                on_click=lambda: event_type_dialog()
                ).classes('text-xs')
    with ui.row().classes('flex flex-col w-full'):
        refresh_event_types()

