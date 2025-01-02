# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator, CellSlotProps

from .generals import theme
import requests
import pandas as pd
import json

import os

from helpers.extensions_import import post_extensions

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

@ui.refreshable
def refresh_extensions():
    extensions = get_extensions()
    table_config= {
            "data":extensions,            
            "locale":"fr-FR",
            "langs":{
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
                {"title": "Extension", "field": "extension", "sorter": "string"},
                {"title": "Name", "field": "name", "sorter": "string"},
                {"title": "Mail", "field": "mail", "sorter": "string"},
                {"title": "Out", "field": "out", "sorter": "string", "formatter":"tickCross","formatterParams":{
                "allowEmpty":"true",
                "allowTruthy":"true",
                "tickElement":"<i class='fa fa-check'></i>",
                "crossElement":"<i class='fa fa-times'></i>",
                }},
                {"title": "Out date", "field": "date_out", "sorter": "date", "formatter": "datetime", "formatterParams": {
                    "inputFormat":"iso",
                    "outputFormat":"dd/MM/yy",
                    "invalidPlaceholder":"(invalid date)",
                    "timezone":os.getenv('TZ'),
                }},
                {"title": "Creation date", "field": "date_added", "sorter": "date", "formatter": "datetime", "formatterParams": {
                    "inputFormat":"iso",
                    "outputFormat":"dd/MM/yy",
                    "invalidPlaceholder":"(invalid date)",
                    "timezone":os.getenv('TZ'),
                }},
                {"title": "Modify date", "field": "date_modified", "sorter": "date", "formatter": "datetime", "formatterParams": {
                    "inputFormat":"iso",
                    "outputFormat":"dd/MM/yy",
                    "invalidPlaceholder":"(invalid date)",
                    "timezone":os.getenv('TZ'),
                }},
                ],
            "layout": "fitColumns",
            "responsiveLayout":True,
            "resizableRows":True,
            "resizableRowGuide": True,
            "pagination":"local",
            "paginationSize":10            
    }
    table = tabulator(table_config).on('cellEdited', update_data_from_table_change).classes('w-full compact').props('id=extensions_table').on_event("rowClick", lambda e: ui.notify(e))

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



async def update_data_from_table_change(e):
    data = e.args
    btn = ui.button('Update', icon='save').classes('text-xs')
    await btn.clicked()
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    webapi_url_extensions = api_base_url + '/v1/extensions'
    
    j = {
        'id': data['id'],
        'extension': data['extension'],
        'name': data['name'],
        'mail': data['mail'],
        'out': data['out']
    }
    
    extensionid = data['id']
    response = requests.patch(
        f"{webapi_url_extensions}/{extensionid}", 
        headers=headers, 
        data=json.dumps(j)
    )
    
    if response.status_code == 200:
        ui.notify('Extensions updated successfully')
        btn.delete()
        ui.tab('Extensions_list').update()
    else:
        ui.notify('Update failed')


async def add_extension(data,dialog):
    #data = e.args["data"]
    ui.notify(f"Add extension {data['extension']} ?")
    print(data)
    btn = ui.button('Validate',icon='save').classes('text-xs')
    await btn.clicked()
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    webapi_url_extensions = api_base_url + '/v1/extensions'
    j = {}
    j['extension'] = data['extension']
    j['name'] = data['name']
    j['mail'] = data['mail']
    j['out'] = data['out']
    js = json.dumps(j)
    response = requests.post(f"{webapi_url_extensions}", headers=headers, data=js)
    if response.status_code == 200:
        ui.notify(f'Extensions added successfully')  # noqa: F541
        dialog.close()
        refresh_extensions.refresh()
        ui.tab('Extensions_list').update()  
    else:
        ui.notify(f'Add failed {response.status_code} {response.content}')  # noqa: F541)
    
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
                with ui.dialog() as dialog, ui.card():
                    data={}
                    ui.label('Extension details')
                    ui.label('Extension')
                    ui.input(label='Extension', on_change=lambda e: data.update({'extension': e.value}))
                    ui.label('Name')
                    ui.input(label='Name', on_change=lambda e: data.update({'name': e.value}))
                    ui.label('Mail')
                    ui.input(label='Mail', on_change=lambda e: data.update({'mail': e.value}))
                    ui.label('Out')
                    ui.select({'False':False,'True':True}, on_change=lambda e: data.update({'out': e.value}))
                    ui.button('Save', on_click=lambda: add_extension(data, dialog)).classes('text-xs')
                ui.button('Add extension', icon='add', on_click=dialog.open).classes('text-xs')
                ui.button('Download CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='extension.csv', filename='extensions.csv',media_type='csv')).classes('text-xs')     
        with ui.tab_panel(Extensions_Import):
            ui.label("Uploader extension list in csv file")            
            ui.upload(label='Upload csv file' ,
                        auto_upload=True,
                        on_upload=read_uploaded_file,
                        on_rejected=lambda: ui.notify('Rejected!'),).props('accept=.csv').classes('max-w-full')
