# -*- coding: UTF-8 -*-
from nicegui import ui, APIRouter
from message import message
import os
import requests

import pandas as pd
import theme

router = APIRouter(prefix='/queues')
api_base_url = os.environ.get('API_URL')

@router.page('/')
def queue_page():
    with theme.frame('- Queues -'):
        message('Queues')
    with ui.tabs().classes('w-full') as tabs:
        Queue_list = ui.tab('Queue List')
        Queue_Import = ui.tab('Queue Import')
        Queue_Add_or_Edit = ui.tab('Queue Add or Edit')

    with ui.tab_panels(tabs, value=Queue_list).classes('w-full'):
            with ui.tab_panel(Queue_list):
                queues = requests.get(f"{api_base_url}/api/v1/queues").json()
                if not queues:
                    headers = ["queue", "queuename"]
                    df = pd.DataFrame(columns=headers)
                    ui.aggrid.from_pandas(df).classes('grid-flow-col')
                else:
                    df = pd.DataFrame(queues)
                    ui.aggrid.from_pandas(df).classes('grid-flow-col')
