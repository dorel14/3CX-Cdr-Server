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
from myhelpers.queues_import import post_queues

router = APIRouter(prefix='/queues')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "queues.csv")

@router.page('/')
def extension_page():
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
        print(b)
        if os.path.exists(data_files):
            os.remove(data_files)
        with open(data_files, "wb") as fcsv:
                fcsv.write(b)
        df = pd.read_csv(data_files, delimiter=",")
        ui.button('Import',icon='upload',on_click=click_import).classes('text-xs')
        ui.aggrid.from_pandas(df).classes('grid-flow-col')
        ui.tab('Queues_Import').update()

    async def update_data_from_table_change(e):
        # ui.notify(f"Update with {e.args['data'] }")
        data = e.args["data"]
        btn = ui.button('Update',icon='save').classes('text-xs')
        await btn.clicked()
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        webapi_url_queues = api_base_url + '/v1/queues'
        j = {}
        j['id'] = data['id']
        j['queue'] = data['queue']
        j['queuename'] = data['queuename']
        js = json.dumps(j)
        queue_id = data['id']
        response = requests.patch(f"{webapi_url_queues}/{queue_id}", headers=headers, data=js)
        if response.status_code == 200:
            ui.notify(f'Queues updated successfully')  # noqa: F541
            btn.delete()
            Queues_list.update()
        else:
            ui.notify(f'Update failed')  # noqa: F541
         
    async def add_queue(data):
        #data = e.args["data"]
        ui.notify(f"Add queue {data['queue']} ?")
        print(data)
        btn = ui.button('Validate',icon='save').classes('text-xs')
        await btn.clicked()
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        webapi_url_queues = api_base_url + '/v1/queues'
        j = {}
        j['queue'] = data['queue']
        j['queuename'] = data['queuename']
        js = json.dumps(j)
        response = requests.post(f"{webapi_url_queues}", headers=headers, data=js)
        if response.status_code == 200:
            ui.notify(f'Queues added successfully')  # noqa: F541
            dialog.close()
            Queues_list.update()  
        else:
            ui.notify(f'Add failed {response.status_code} {response.content}')  # noqa: F541)
    

    ui.page_title("3CX CDR Server app - Queues")    
    with theme.frame('- Queues -'):
        ui.label('')
        #message('Queues')
    with ui.tabs().classes('w-full') as tabs:
        Queues_list = ui.tab('Queues List')
        Queues_Import = ui.tab('Queues Import')
    ui.label('Queues informations are editable in the table below.')  
    with ui.tab_panels(tabs, value=Queues_list).classes('w-full'):
              
        with ui.tab_panel(Queues_list):
            queues = requests.get(f"{api_base_url}/api/v1/queues").json()
            if not queues:
                headers = ["queue", "name", "mail"]
                df = pd.DataFrame(columns=headers)
                df.to_csv(path_or_buf='queue.csv', index=False)
                ui.button('Download template CSV',
                          icon='download',
                          on_click=lambda: ui.download(src='queues.csv',filename='queues.csv',media_type='csv')).classes('ml-auto text-xs')
                ui.aggrid().from_pandas(df).classes('grid-flow-col')
            else:
                df = pd.DataFrame(queues)
                column_defs = []
                for column in df.columns:
                    col_def = {'headerName': column.capitalize(), 'field': column}
                    col_def['sortable'] = 'true'
                    col_def['filter'] = 'true'
                    if df[column].dtype in ['int64', 'float64']:
                         col_def['type'] = 'numericColumn',
                         col_def['filter'] = 'agNumberColumnFilter'
                         col_def['floatingFilter']= False
                    else :
                         col_def['type'] = 'textColumn'
                         col_def['filter'] = 'agTextColumnFilter'
                         col_def['floatingFilter']= False
                    if df[column].dtype == 'datetime64[ns]':
                         col_def['type'] = 'datetimeColumn'
                         col_def['filter'] = 'agDateColumnFilter'
                         col_def['floatingFilter']= False
                    if df[column].dtype == 'bool':
                         col_def['filter'] = 'agBooleanColumnFilter'
                         col_def['floatingFilter']= False
                    if column == 'id':
                         col_def['pinned'] = 'left'
                         col_def['width']= 50
                    if column in ['queue', 'queuename']:
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
                df.to_csv(path_or_buf='queue.csv', index=False)                
                table = ui.aggrid.from_pandas(df, options=grid_options).classes('grid-flow-col').on("cellValueChanged", update_data_from_table_change)
                with ui.dialog() as dialog, ui.card():
                    data={}
                    ui.label('Queue details')
                    ui.label('Queue')
                    ui.input(label='Queue', on_change=lambda e: data.update({'queue': e.value}))
                    ui.label('Name')
                    ui.input(label='Name', on_change=lambda e: data.update({'queuename': e.value}))
                    ui.button('Save', on_click=lambda: add_queue(data)).classes('text-xs')
                ui.button('Add queue', icon='add', on_click=dialog.open).classes('text-xs')
                ui.button('Download CSV',
                          icon='download',
                          on_click=lambda: ui.download(src='queue.csv', filename='queue.csv',media_type='csv')).classes('text-xs')     
        with ui.tab_panel(Queues_Import):
            ui.label("Upload queue list in csv file")            
            ui.upload(label='Upload csv file' ,
                      auto_upload=True,
                      on_upload=read_uploaded_file,
                      on_rejected=lambda: ui.notify('Rejected!'),).props('accept=.csv').classes('max-w-full')
            
            
