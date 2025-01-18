# -*- coding: UTF-8 -*-

from gc import enable
from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator
from datetime import datetime
import pytz
from .generals import theme
import requests
import pandas as pd
import json
import os

from helpers.queues_import import post_queues

# Set timezone according to environment variable
timezone = pytz.timezone(os.getenv('TZ', 'Europe/Paris'))
router = APIRouter(prefix='/queues')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "queues.csv")

# Add error handling for the API call
def get_queues():
    try:
        response =  requests.get(f"{api_base_url}/v1/queues")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        ui.notify(f"Error fetching queues: {str(e)}", type='negative')
        return []
def get_extensions():
    try:
        response =  requests.get(f"{api_base_url}/v1/extensions")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        ui.notify(f"Error fetching extensions: {str(e)}", type='negative')
        return []

@ui.refreshable
def refresh_queues():
    queues = get_queues()

    def format_date(date_str):
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            local_date = date_obj.astimezone(timezone)
            return local_date.strftime('%d/%m/%Y')
        return ''
    
    with ui.grid(columns=5).classes('w-full col-span-5 flex-nowrap'):
        # Headers
        ui.label('').classes('font-bold')
        ui.label('Number').classes('font-bold')
        ui.label('Name').classes('font-bold')
        ui.label('Created').classes('font-bold')
        ui.label('Modified').classes('font-bold')
    with ui.scroll_area().classes('w-full h-dvh'):
        for queue in queues:
            if queue['extensionslist']:
                with ui.expansion(group='group').classes('w-full ') as expansion:
                    with expansion.add_slot('header'):                    
                        with ui.grid(columns=5).classes('w-full col-span-5 flex-nowrap'):
                            with ui.button_group().props('outline'):
                                ui.button(icon='mode_edit', on_click=lambda queue=queue: handle_row_click({'row': queue})
                                        ).classes('text-xs text-center size-10')
                                ui.button(icon='delete').classes('text-xs text-center size-10')           # Queue row
                            ui.label(queue['queue'])
                            ui.label(queue['queuename'])
                            ui.label(format_date(queue['date_added']))
                            ui.label(format_date(queue['date_modified']))
                    # Extensions subgrid
                    table_config = {
                        "data": queue['extensionslist'],
                            "layout": "fitColumns",
                            "columns": [
                                {"title": "Extension", "field": "extension"},
                                {"title": "Name", "field": "name"},
                            ],
                            "pagination": "local",
                            "paginationSize": 10,
                            "paginationSizeSelector": [10, 20, 50, 100],
                        }
                    table = tabulator(table_config).classes('w-full compact')
            else:
                with ui.grid(columns=5).classes('w-full col-span-5 flex-nowrap'):
                    with ui.button_group().props('outline'):
                        ui.button(icon='mode_edit', on_click=lambda queue=queue: handle_row_click({'row': queue})
                                ).classes('text-xs text-center size-10')
                        ui.button(icon='delete').classes('text-xs text-center size-10')         # Queue row
                    ui.label(queue['queue'])
                    ui.label(queue['queuename'])
                    ui.label(format_date(queue['date_added']))
                    ui.label(format_date(queue['date_modified']))

async def click_import():
    response = await run.io_bound(post_queues, data_files)
    ui.notify(f'Queues {response}')
    ui.tab('Queues_list').update()

def read_uploaded_file(e: events.UploadEventArguments):
    ui.notify('File uploaded successfully!')
    if not os.path.exists(data_folder):
                os.makedirs(data_folder, exist_ok=True)
    b = e.content.read()
        # Read the uploaded file
    if os.path.exists(data_files):
        os.remove(data_files)
    with open(data_files, "wb") as fcsv:
            fcsv.write(b)
    df = pd.read_csv(data_files, delimiter=",")
    print(df)
    csv_table_config = {
        "data":df.to_dict('records'),
        "columns": [{"field": col, "title": col} for col in df.columns],
        "layout": "fitColumns",
        "responsiveLayout":True,
        "resizableRows":True,
        "resizableRowGuide": True,
        "pagination":"local",
        "paginationSize":10
    }
    with ui.column().classes('w-full'):
        csv_table = tabulator(csv_table_config).classes('w-full compact').props('id=csv_queues_table')
        ui.button('Import',icon='upload',on_click=click_import).classes('text-xs')
        ui.button('Cancel',icon='cancel',on_click=lambda: ui.navigate.reload('/queues'))
        ui.tab('Queues_Import').update()

async def queue_dialog(row_data=None):
    dialog = ui.dialog()
    data = {}
    
    if row_data:
        data = row_data
        data['extensions'] = [{'id': e['id']} for e in data.get('extensionslist', [])]
        assigned_extensions = [e['id'] for e in data['extensions']]
    else:
        data['extensions'] = []
        assigned_extensions = []

    with dialog, ui.card().classes('w-1/3'):
        ui.label('Queue details')
        with ui.row().classes('flex-wrap'):
            number_input = ui.input(
                label='Number', 
                value=data.get('queue', ''),
                on_change=lambda e: data.update({'queue': e.value})
            )
            name_input = ui.input(
                label='Name', 
                value=data.get('queuename', ''),
                on_change=lambda e: data.update({'queuename': e.value})
            )
        
        ui.label('Extensions:').classes('mt-4 font-bold')
        extensions = get_extensions()
        if isinstance(extensions, list):
            extensions = {e['id']: e['name'] for e in extensions}
        available_extensions = {k: v for k, v in extensions.items() if k not in assigned_extensions}

        ui.select(options=available_extensions, multiple=True).on_value_change(
            lambda e: data.update({'extensions': [{'id': ext_id} for ext_id in e.value]})
        ).classes('w-full')
        
        with ui.row():
            for ext_id in assigned_extensions:
                ui.chip(
                    text=f"{extensions.get(ext_id, '')}",
                    removable=True,
                    color='white'
                ).on(
                    'remove',
                    lambda e, ext_id=ext_id: handle_extension_removal(ext_id, data)
                ).classes('text-xs')

        async def handle_extension_removal(extension_id, data):
            data['extensions'] = [ext for ext in data['extensions'] if ext['id'] != extension_id]
            await requests.delete(f"{api_base_url}/v1/queues/{data['id']}/extension/{extension_id}")
            print(f"Current extensions: {data['extensions']}")

        def handle_save():
            save_data = {
                'queue': data.get('queue'),
                'queuename': data.get('queuename'),
                'extensionslist': data.get('extensions')
            }
            
            if data.get('id'):
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.patch(
                    f"{api_base_url}/v1/queues/{data['id']}", 
                    headers=headers,
                    data=json.dumps(save_data)
                )
                print(response)
            else:
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.post(
                    f"{api_base_url}/v1/queues",
                    headers=headers,
                    data=json.dumps(save_data)
                )
                print(response)
            if response.status_code == 200:
                ui.notify('Queue saved successfully', type='positive')
                dialog.close()
                refresh_queues.refresh()
            else:
                ui.notify(f'Operation failed: {response.status_code} {response.content}')
                
        with ui.row().classes('w-full justify-end'):
            ui.button('Save', on_click=handle_save).classes('text-xs')
            ui.button('Cancel', on_click=dialog.close).classes('text-xs')
    
    dialog.open()

# Update the table row click handler
async def handle_row_click(e):
    print("Row clicked:", e['row'])  # Debug
    row_data = e['row']
    await queue_dialog(row_data)
    
@router.page('/')
def queue_page():
    ui.page_title("3CX CDR Server app - Queues")    
    with theme.frame('- Queues -'):
        ui.label('')
    with ui.tabs().classes('w-full') as tabs:
        Queues_list = ui.tab('Queues List')
        Queues_Import = ui.tab('Queues Import')
    ui.label('Queue informations are editable on pencil button.')  
    with ui.tab_panels(tabs, value=Queues_list).classes('w-full'):
        with ui.tab_panel(Queues_list):
            queues = get_queues()
            if not queues:
                headers = ["queue", "queuename"]
                emptydf = pd.DataFrame(columns=headers)
                emptydf.to_csv(path_or_buf='queues.csv', index=False)
                emptycsv_table_config = {
                    "data":emptydf.to_dict('records'),
                    "columns": [{"field": col, "title": col} for col in emptydf.columns],
                    "layout": "fitColumns",
                    "responsiveLayout":True,
                    "resizableRows":True,
                    "resizableRowGuide": True,
                    "pagination":"local",
                    "paginationSize":10
                }
                emptycsv_table = tabulator(emptycsv_table_config).props('id=empty_queues_table').classes('w-full compact')
                ui.button('Download template CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='queues.csv',filename='queues.csv',media_type='csv')
                            ).classes('ml-auto text-xs')

            else:
                with ui.row().classes('w-full border-b pb-2'):            
                    ui.button('Add queue', icon='add', on_click=lambda: queue_dialog()).classes('text-xs')
                    ui.button('Download CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='queues.csv', filename='queues.csv',media_type='csv')).classes('text-xs')
                refresh_queues()    
        with ui.tab_panel(Queues_Import):
            ui.label("Uploader queue list in csv file")            
            ui.upload(label='Upload csv file' ,
                        auto_upload=True,
                        on_upload=read_uploaded_file,
                        on_rejected=lambda: ui.notify('Rejected!'),).props('accept=.csv').classes('max-w-full')
