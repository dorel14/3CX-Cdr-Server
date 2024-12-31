# -*- coding: UTF-8 -*-

from nicegui import ui, APIRouter, events, run
from nicegui_tabulator import tabulator
from .generals import message  # noqa: F401
from .generals import theme
import requests
import pandas as pd
import json
import sys
import os
sys.path.append(os.path.abspath("."))
from ..helpers.queues_import import post_queues

router = APIRouter(prefix='/queues')
api_base_url = os.environ.get('API_URL')
data_folder = "/data/files"
data_files = os.path.join(data_folder, "queues.csv")

def get_queues():
    url = f'{api_base_url}/v1/queues'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

@ui.refreshable
def refresh_queues():
    queues = get_queues()
    df = pd.DataFrame(queues)

    columns = []

    for column in df.columns:
        col_def = {
            'title': column.capitalize(),
            'field': column,
            'sorter': True,
            'headerFilter': True
        }
        
        if df[column].dtype in ['int64', 'float64']:
            col_def['sorter'] = 'number'
            
        if column == 'id':
            col_def['frozen'] = True
            col_def['width'] = 50
            
        if column in ['queuename', 'queue']:
            col_def['editor'] = True
            
        columns.append(col_def)
    table_config= {
            "data":queues,
            "locale":os.getenv('LOCALE_LANGUAGE', 'fr-FR'),
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
            "autoColumns":False,
            "layout": "fitDataTable",
            "responsiveLayout":True,
            "resizableRows":True,
            "resizableRowGuide": True,
            "pagination":"local",
            "paginationSize":10            
    }
    table = tabulator(
        table_config
    ).on('cellEdited', update_data_from_table_change)

async def click_import():
    response = await run.io_bound(post_queues, data_files)
    ui.notify(f'queues {response}')
    ui.tab('queues_list').update()

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
    ui.button('Import', icon='upload', on_click=click_import).classes('text-xs')
    #tabulator(df, layout='fitColumns', height='400px')
    ui.tab('queues_Import').update()

async def update_data_from_table_change(e):
    data = e.args
    btn = ui.button('Update', icon='save').classes('text-xs')
    await btn.clicked()
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    webapi_url_queues = api_base_url + '/v1/queues'
    
    j = {
        'id': data['id'],
        'queue': data['queue'],
        'queuename': data['queuename']
    }
    
    queueid = data['id']
    response = requests.patch(
        f"{webapi_url_queues}/{queueid}", 
        headers=headers, 
        data=json.dumps(j)
    )
    
    if response.status_code == 200:
        ui.notify('Queues updated successfully')
        btn.delete()
        ui.tab('queues_list').update()
    else:
        ui.notify('Update failed')


async def add_queue(data,dialog):
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
        ui.notify(f'queues added successfully')  # noqa: F541
        dialog.close()
        refresh_queues.refresh()
        ui.tab('queues_list').update()  
    else:
        ui.notify(f'Add failed {response.status_code} {response.content}')  # noqa: F541)
    
@router.page('/')
def queue_page():
    ui.page_title("3CX CDR Server app - Queues")    
    with theme.frame('- Queues -'):
        ui.label('')
        #message('queues')
    with ui.tabs().classes('w-full') as tabs:
        queues_list = ui.tab('Queues List')
        queues_Import = ui.tab('Queues Import')
    ui.label('Queues informations are editable in the table below.')  
    with ui.tab_panels(tabs, value=queues_list).classes('w-full'):

        with ui.tab_panel(queues_list):
            queues = get_queues()
            if not queues:
                headers = ["queue", "queuename"]
                emptydf = pd.DataFrame(columns=headers)
                emptydf.to_csv(path_or_buf='queues.csv', index=False)
                ui.button('Download template CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='queues.csv',filename='queues.csv',media_type='csv')).classes('ml-auto text-xs')
                tabulator(emptydf, layout='fitColumns', height='400px')
            else:
                refresh_queues()
                with ui.dialog() as dialog, ui.card():
                    data={}
                    ui.label('Queue details')
                    ui.label('Queue')
                    ui.input(label='Queue', on_change=lambda e: data.update({'queue': e.value}))
                    ui.label('Name')
                    ui.input(label='Queue Name', on_change=lambda e: data.update({'queuename': e.value}))
                    ui.button('Save', on_click=lambda: add_queue(data, dialog)).classes('text-xs')
                ui.button('Add queue', icon='add', on_click=dialog.open).classes('text-xs')
                ui.button('Download CSV',
                            icon='download',
                            on_click=lambda: ui.download(src='queue.csv', filename='queues.csv',media_type='csv')).classes('text-xs')     
        with ui.tab_panel(queues_Import):
            ui.label("Uploader queue list in csv file")            
            ui.upload(label='Upload csv file' ,
                        auto_upload=True,
                        on_upload=read_uploaded_file,
                        on_rejected=lambda: ui.notify('Rejected!'),).props('accept=.csv').classes('max-w-full')
            
            
