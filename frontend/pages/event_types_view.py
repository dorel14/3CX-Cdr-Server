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

router = APIRouter(prefix='/event_types')
api_base_url = os.environ.get('API_URL')


@router.page('/')
def parameters_view():
    ui.page_title("3CX CDR Server app - Event Types")    
    with theme.frame('- Event Types -'):
        ui.label('Event Types')