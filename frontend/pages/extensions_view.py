# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator
from datetime import datetime
import pytz
from .generals import theme
import requests
import pandas as pd
import json

import os

from helpers.extensions_import import post_extensions
# Set timezone according to environment variable
timezone = pytz.timezone(os.getenv('TZ', 'Europe/Paris'))
router = APIRouter(prefix='/extensions')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "extensions.csv")

# Add error handling for the API call
def get_extensions():
    try:
        response = requests.get(f"{api_base_url}/v1/extensions")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        ui.notify(f"Error fetching extensions: {str(e)}", type='negative')
        return []

def get_queues():
    try:
        response = requests.get(f"{api_base_url}/v1/queues")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        ui.notify(f"Error fetching queues: {str(e)}", type='negative')
        return []

@ui.refreshable
def refresh_extensions():
    extensions = get_extensions()

    def format_date(date_str):
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            local_date = date_obj.astimezone(timezone)
            return local_date.strftime('%d/%m/%Y')
        return ''
    
    with ui.grid(columns=6).classes('w-full'):
        # Headers
        ui.label('').classes('font-bold')
        ui.label('Name').classes('font-bold')
        ui.label('Extension').classes('font-bold')
        ui.label('Mail').classes('font-bold')
        ui.label('Out').classes('font-bold')
        ui.label('Created').classes('font-bold')
        ui.label('Modified').classes('font-bold')

        for ext in extensions:
            with ui.expansion(group='group').classes('w-full col-span-6 flex-wrap') as expansion:
                with expansion.add_slot('header'):                    
                    with ui.grid(columns=7).classes('w-full'):
                        ui.button(icon='mode_edit', on_click=lambda ext=ext: handle_row_click({'row': ext})).classes('text-xs text-center size-10')            # Extension row
                        ui.label(ext['name'])
                        ui.label(ext['extension'])
                        ui.label(ext['mail'])
                        ui.label( '✗' if ext['out'] else '✓').classes('text-red-500 text-center' if ext['out'] else 'text-green-500 text-center')
                        ui.label(format_date(ext['date_added']))
                        ui.label(format_date(ext['date_modified']))

                    # Queues subgrid
                if ext['queueslist']:
                    with ui.grid(columns=3).classes('w-full mt-2 ml-4'):
                        # Queue headers
                        ui.label('Queue').classes('font-bold')
                        ui.label('Queue name').classes('font-bold')
                        ui.label('Added date').classes('font-bold')

                        for queue in ext['queueslist']:
                            with ui.grid(columns=3).classes('w-full mt-2 ml-4'):
                                ui.label(queue['queue'])
                                ui.label(queue['queuename'])
                                ui.label(format_date(queue['date_added']))



async def click_import():
    response = await run.io_bound(post_extensions, data_files)
    ui.notify(f'Extensions {response}')
    ui.tab('Extensions_list').update()


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
        csv_table = tabulator(csv_table_config).classes('w-full compact').props('id=csv_extensions_table')
        ui.button('Import',icon='upload',on_click=click_import).classes('text-xs')
        ui.button('Cancel',icon='cancel',on_click=lambda: ui.navigate.reload('/extensions'))
        ui.tab('Extensions_Import').update()


async def extension_dialog(row_data=None):
    dialog = ui.dialog()
    data = {}
    
    if row_data:
        data = row_data.get('row', {})
        # Initialize queues list with current assignments at dialog creation
        data['queues'] = [q['id'] for q in data.get('queueslist', [])]
        assigned_queues = data['queues']
    else:
        data['queues'] = []
        assigned_queues = []

    with dialog, ui.card().classes('w-1/3'):
        ui.label('Extension details')
        with ui.row().classes('flex-wrap'):
            extension_input = ui.input(
                label='Extension', 
                value=data.get('extension', ''),
                on_change=lambda e: data.update({'extension': e.value})
            )
            name_input = ui.input(
                label='Name', 
                value=data.get('name', ''),
                on_change=lambda e: data.update({'name': e.value})
            )
        with ui.row().classes('flex-wrap'):
            mail_input = ui.input(
                label='Mail', 
                value=data.get('mail', ''),
                on_change=lambda e: data.update({'mail': e.value})
            )
            out_select = ui.checkbox(
                'Out',
                value=data.get('out', False),
                on_change=lambda e: data.update({'out': e.value})
            )
        
        # Display all queues with checkboxes
        ui.label('Queues:').classes('mt-4 font-bold')
        queues = get_queues()
        
        with ui.column().classes('w-full'):
            current_row = None
            for i, queue in enumerate(queues):
                if i % 3 == 0:
                    current_row = ui.row().classes('w-full justify-start')
                with current_row:
                    is_assigned = queue['id'] in assigned_queues
                    ui.checkbox(
                        f"{queue['queue']} - {queue['queuename']}", 
                        value=is_assigned,
                        on_change=lambda e, q_id=queue['id']: handle_queue_selection(e, q_id, data)
                    ).classes('mr-4')

        def handle_queue_selection(e, queue_id, data):
            if e.value and queue_id not in data['queues']:
                data['queues'].append(queue_id)
            elif not e.value and queue_id in data['queues']:
                data['queues'].remove(queue_id)
            print(f"Current queues: {data['queues']}")  # Debug print
        
        async def handle_save():
            save_data = {
                'extension': data.get('extension'),
                'name': data.get('name'),
                'mail': data.get('mail'),
                'out': data.get('out'),
                'queues': [{'id': q_id} for q_id in data['queues']]
            }
            
            if data.get('id'):
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.patch(
                    f"{api_base_url}/v1/extensions/{data['id']}", 
                    headers=headers,
                    data=json.dumps(save_data)
                )
            else:
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.post(
                    f"{api_base_url}/v1/extensions",
                    headers=headers,
                    data=json.dumps(save_data)
                )
                
            if response.status_code == 200:
                ui.notify('Extension saved successfully')
                dialog.close()
                refresh_extensions.refresh()
            else:
                ui.notify(f'Operation failed: {response.status_code} {response.content}')
                
        ui.button('Save', on_click=handle_save).classes('text-xs')
        ui.button('Cancel', on_click=dialog.close).classes('text-xs')
    
    dialog.open()


# Update the table row click handler
async def handle_row_click(e):
    print("Row clicked:", e['row'])  # Debug
    row_data = e['row']
    await extension_dialog(row_data)
    
@router.page('/')
def extension_page():
    ui.page_title("3CX CDR Server app - Extensions")    
    with theme.frame('- Extensions -'):
        ui.label('')
        #message('Extensions')
    with ui.tabs().classes('w-full') as tabs:
        Extensions_list = ui.tab('Extensions List')
        Extensions_Import = ui.tab('Extensions Import')
    ui.label('Extensions informations are editable in the table below.')  
    with ui.tab_panels(tabs, value=Extensions_list).classes('w-full'):
        with ui.tab_panel(Extensions_list):
            extensions = get_extensions()
            if not extensions:
                headers = ["extension", "name", "mail"]
                emptydf = pd.DataFrame(columns=headers)
                emptydf.to_csv(path_or_buf='extensions.csv', index=False)
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
                emptycsv_table = tabulator(emptycsv_table_config).props('id=empty_extensions_table').classes('w-full compact')
                ui.button('Download template CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='extensions.csv',filename='extensions.csv',media_type='csv')).classes('ml-auto text-xs')

            else:
                refresh_extensions()                
                ui.button('Add extension', icon='add', on_click=lambda: extension_dialog()).classes('text-xs')
                ui.button('Download CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='extension.csv', filename='extensions.csv',media_type='csv')).classes('text-xs')     
        with ui.tab_panel(Extensions_Import):
            ui.label("Uploader extension list in csv file")            
            ui.upload(label='Upload csv file' ,
                        auto_upload=True,
                        on_upload=read_uploaded_file,
                        on_rejected=lambda: ui.notify('Rejected!'),).props('accept=.csv').classes('max-w-full')
