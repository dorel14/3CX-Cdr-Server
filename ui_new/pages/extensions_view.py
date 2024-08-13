# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from message import message  # noqa: F401
import theme
import requests
import pandas as pd
import json
import sys
import os
sys.path.append(os.path.abspath("."))
from myhelpers.extensions_import import post_extensions

router = APIRouter(prefix='/extensions')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "extensions.csv")


@ui.refreshable
def refresh_extensions():
    extensions = requests.get(f"{api_base_url}/api/v1/extensions").json()
    df = pd.DataFrame(extensions)
    column_defs = []
    for column in df.columns:
        col_def = {'headerName': column.capitalize(), 'field': column}
        col_def['sortable'] = 'true'
        col_def['filter'] = 'true'
        col_def['floatingFilter'] = 'False'
        if df[column].dtype in ['int64', 'float64']:
            col_def['type'] = 'numericColumn',
            col_def['filter'] = 'agNumberColumnFilter'
        else :
            col_def['type'] = 'textColumn'
            col_def['filter'] = 'agTextColumnFilter'
        if df[column].dtype == 'datetime64[ns]':
            col_def['type'] = 'datetimeColumn'
            col_def['filter'] = 'agDateColumnFilter'
        if df[column].dtype == 'bool':
            col_def['filter'] = 'agBooleanColumnFilter'
        if column == 'id':
            col_def['pinned'] = 'left'
            col_def['width']= 50
        if column in ['name', 'mail', 'out']:
            col_def['editable']= True
        column_defs.append(col_def)
    grid_options = {
        'columnDefs': column_defs,
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
    ui.aggrid.from_pandas(df, options=grid_options).classes('grid-flow-col').on("cellValueChanged", update_data_from_table_change)

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
    print(b)
    if os.path.exists(data_files):
        os.remove(data_files)
    with open(data_files, "wb") as fcsv:
            fcsv.write(b)
    df = pd.read_csv(data_files, delimiter=",")
    ui.button('Import',icon='upload',on_click=click_import).classes('text-xs')
    ui.aggrid.from_pandas(df).classes('grid-flow-col')
    ui.tab('Extensions_Import').update()

async def update_data_from_table_change(e):
    # ui.notify(f"Update with {e.args['data'] }")
    data = e.args["data"]
    btn = ui.button('Update',icon='save').classes('text-xs')
    await btn.clicked()
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    webapi_url_extensions = api_base_url + '/v1/extensions'
    j = {}
    j['id'] = data['id']
    j['extension'] = data['extension']
    j['name'] = data['name']
    j['mail'] = data['mail']
    j['out'] = data['out']
    js = json.dumps(j)
    extensionid = data['id']
    response = requests.patch(f"{webapi_url_extensions}/{extensionid}", headers=headers, data=js)
    if response.status_code == 200:
        ui.notify(f'Extensions updated successfully')  # noqa: F541
        btn.delete()
        ui.tab('Extensions_list').update()
    else:
        ui.notify(f'Update failed')  # noqa: F541

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
            extensions = requests.get(f"{api_base_url}/api/v1/extensions").json()
            if not extensions:
                headers = ["extension", "name", "mail"]
                emptydf = pd.DataFrame(columns=headers)
                emptydf.to_csv(path_or_buf='extension.csv', index=False)
                ui.button('Download template CSV',
                          icon='download',
                          on_click=lambda: ui.download(src='extensions.csv',filename='extensions.csv',media_type='csv')).classes('ml-auto text-xs')
                ui.aggrid().from_pandas(emptydf).classes('grid-flow-col')
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
            
            
