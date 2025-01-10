# -*- coding: UTF-8 -*-

from pathlib import Path
from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator

from .generals import theme
from helpers.queues_import import post_queues

import requests
import pandas as pd
import json
import os

router = APIRouter(prefix='/queues')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "queues.csv")



def get_queues():
    try:
        response = requests.get(f"{api_base_url}/v1/queues")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        ui.notify(f"Error fetching queues: {str(e)}", type='negative')
        return []

@ui.refreshable
def refresh_queues():
    queues = get_queues()
    ui.add_head_html(f'''<script>{(Path(__file__).parent / 'javascript' / 'togglerow.js').read_text()}</script>''')     
    table_config = {
        "data": queues,
        "locale": "fr-FR",
        "langs": {
            'fr-FR': {
                'pagination': {
                    'first': 'Premier',
                    'first_title': 'Première Page',
                    'last': 'Dernier',
                    'last_title': 'Dernière Page',
                    'prev': 'Précédent',
                    'prev_title': 'Page Précédente',
                    'next': 'Suivant',
                    'next_title': 'Page Suivante',
                    'all': 'Tout'
                },
            }
        },
        "columns": [
            {
                "formatter":"""hideIcon, align:"center", title:"Hide Sub", headerSort:false, cellClick:function(e, row, formatterParams){
                                const id = row.getData().id;
                                $(".subTable" + id + "").toggle();"""
            },
            {"title": "Number", "field": "queue", "sorter": "string"},
            {"title": "Name", "field": "queuename", "sorter": "string"},
            {"title": "Creation date", "field": "date_added", "sorter": "date", "formatter": "datetime", 
            "formatterParams": {
                "inputFormat": "iso",
                "outputFormat": "dd/MM/yy",
                "invalidPlaceholder": "(invalid date)",
                "timezone": os.getenv('TZ'),
            }},
            {"title": "Modify date", "field": "date_modified", "sorter": "date", "formatter": "datetime",
            "formatterParams": {
                "inputFormat": "iso",
                "outputFormat": "dd/MM/yy",
                "invalidPlaceholder": "(invalid date)",
                "timezone": os.getenv('TZ'),
            }},
        ],
        ":rowFormatter": r"""
            function(row) {
                if(row.getData().extensionslist && row.getData().extensionslist.length > 0) {
                    var holderEl = document.createElement("div");
                    var tableEl = document.createElement("div");
                    
                    holderEl.style.padding = "10px";
                    holderEl.style.backgroundColor = "#f5f5f5";
                    holderEl.style.marginTop = "5px";
                    holderEl.style.width = "100%";
                    
                    holderEl.appendChild(tableEl);
                    

                    tableEl.style.border = "1px solid #333";

                    var element = row.getElement();
                    var detailsEl = document.createElement("div");
                    detailsEl.style.boxSizing = "border-box";
                    detailsEl.style.padding = "10px";
                    detailsEl.appendChild(holderEl);
                    
                    element.after(detailsEl);
                    
                    var subTable = new Tabulator(tableEl, {
                        layout: "fitColumns",
                        data: row.getData().extensionslist,
                        columns: [
                            {title: "Extension", field: "extension", width: 150},
                            {title: "Name", field: "name", width: 200},
                            {title: "Added", field: "date_added", formatter: "datetime", 
                            formatterParams: {
                                outputFormat: "dd/MM/yy"
                            },
                            width: 150
                            }
                        ]
                    });
                }
            }
        """,
        "layout": "fitColumns",
        "responsiveLayout": True,
        "resizableRows": True,
        "resizableRowGuide": True,
        "pagination": "local",
        "paginationSize": 10
    }
    table = tabulator(table_config).classes('w-full compact').props('id=queues_table').on_event("rowClick", lambda e: handle_row_click(e))

async def click_import():
    response = await run.io_bound(post_queues, data_files)
    ui.notify(f'Queues {response}')
    ui.tab('Queues_list').update()

def read_uploaded_file(e: events.UploadEventArguments):
    ui.notify('File uploaded successfully!')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder, exist_ok=True)
    
    b = e.content.read()
    if os.path.exists(data_files):
        os.remove(data_files)
    with open(data_files, "wb") as fcsv:
        fcsv.write(b)
    
    df = pd.read_csv(data_files, delimiter=",")
    csv_table_config = {
        "data": df.to_dict('records'),
        "columns": [{"field": col, "title": col} for col in df.columns],
        "layout": "fitColumns",
        "responsiveLayout": True,
        "resizableRows": True,
        "resizableRowGuide": True,
        "pagination": "local",
        "paginationSize": 10
    }
    with ui.column().classes('w-full'):
        csv_table = tabulator(csv_table_config).classes('w-full compact').props('id=csv_queues_table')
        ui.button('Import', icon='upload', on_click=click_import).classes('text-xs')
        ui.button('Cancel', icon='cancel', on_click=lambda: ui.navigate.reload('/queues'))
        ui.tab('Queues_Import').update()

async def queue_dialog(row_data=None):
    dialog = ui.dialog()
    data = {}
    
    if row_data:
        data = row_data.get('row', {})

    with dialog, ui.card():
        ui.label('Queue details')
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
        
        async def handle_save():
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            if data.get('id'):
                response = requests.patch(
                    f"{api_base_url}/v1/queues/{data['id']}", 
                    headers=headers,
                    data=json.dumps(data)
                )
            else:
                response = requests.post(
                    f"{api_base_url}/v1/queues",
                    headers=headers,
                    data=json.dumps(data)
                )
            
            if response.status_code == 200:
                ui.notify('Queue saved successfully')
                dialog.close()
                refresh_queues.refresh()
            else:
                ui.notify(f'Operation failed: {response.status_code} {response.content}')
        
        ui.button('Save', on_click=handle_save).classes('text-xs')
    
    dialog.open()

async def handle_row_click(e):
    row_data = e.args
    await queue_dialog(row_data)

@router.page('/')
def queue_page():
    ui.page_title("3CX CDR Server app - Queues")
    with theme.frame('- Queues -'):
        ui.label('')
    
    with ui.tabs().classes('w-full') as tabs:
        Queues_list = ui.tab('Queues List')
        Queues_Import = ui.tab('Queues Import')
    
    ui.label('Queue informations are editable in the table below.')
    
    with ui.tab_panels(tabs, value=Queues_list).classes('w-full'):
        with ui.tab_panel(Queues_list):
            queues = get_queues()
            if not queues:
                headers = ["number", "name"]
                emptydf = pd.DataFrame(columns=headers)
                emptydf.to_csv(path_or_buf='queues.csv', index=False)
                emptycsv_table_config = {
                    "data": emptydf.to_dict('records'),
                    "columns": [{"field": col, "title": col} for col in emptydf.columns],
                    "layout": "fitColumns",
                    "responsiveLayout": True,
                    "resizableRows": True,
                    "resizableRowGuide": True,
                    "pagination": "local",
                    "paginationSize": 10
                }
                emptycsv_table = tabulator(emptycsv_table_config).props('id=empty_queues_table').classes('w-full compact')
                ui.button('Download template CSV',
                        icon='download',
                        on_click=lambda: ui.download(src='queues.csv', filename='queues.csv', media_type='csv')).classes('ml-auto text-xs')
            else:
                refresh_queues()
                ui.button('Add Queue', icon='add', on_click=lambda: queue_dialog()).classes('text-xs')
                ui.button('Download CSV',
                        icon='download',
                        on_click=lambda: ui.download(src='queues.csv', filename='queues.csv', media_type='csv')).classes('text-xs')
        
        with ui.tab_panel(Queues_Import):
            ui.label("Upload queue list in csv file")
            ui.upload(label='Upload csv file',
                    auto_upload=True,
                    on_upload=read_uploaded_file,
                    on_rejected=lambda: ui.notify('Rejected!')).props('accept=.csv').classes('max-w-full')
