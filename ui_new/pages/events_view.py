# -*- coding: UTF-8 -*-
from fullcalendar.FullCalendar import FullCalendar as fullcalendar
from nicegui import ui, APIRouter, events, run
from message import message  # noqa: F401
import theme
import requests
import pandas as pd
import json
import sys
import os
from datetime import datetime




sys.path.append(os.path.abspath("."))


router = APIRouter(prefix='/events')
api_base_url = os.environ.get('API_URL')
impact_colors={
    '0': 'blue',
    '1': 'green',
    '2': 'orange',
    '3': 'red',
    '4': 'black',
}
impact_levels={
        '0': 'None',
        '1': 'Low',
        '2': 'Medium',
        '3': 'Hihgh',
        '4': 'Critical',
    }




def handle_click(event: events.GenericEventArguments):
    if 'info' in event.args:
        ui.notify(event.args['info']['event'])

def get_events():
    url = f'{api_base_url}/api/v1/extra_events'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        events = []
        for event in data:
                events.append({
                    'id': event['id'],
                    'title': event['event_title'],
                    'start': event['event_start'],
                    'end': event['event_end'],
                    'description':event['event_explanation'],
                    'impact':impact_levels[event['event_impact']],
                    'color': impact_colors[event['event_impact']],
            }
            )
        print()
        return events
    else:
        return []

@router.page('/')
def events_view():
    ui.page_title("3CX CDR Server app - Events")    
    with theme.frame('- Events -'):
        ui.label('')
        #message('Extensions')
    options = {
    'locale': os.environ.get('LOCALE_LANGUAGE').split('_')[0],
    'initialView': 'dayGridMonth',
    'headerToolbar': {'left': 'title','right': 'dayGridYear, dayGridMonth, dayGridWeek, dayGridDay'},
    'footerToolbar': {'right': 'prev,next today'},
    'slotMinTime': '05:00:00',
    'slotMaxTime': '22:00:00',
    'allDaySlot': False,
    'timeZone': os.environ.get('TZ'),
    'height': 'auto',
    'width': 'auto',
    'events': get_events(),
}
    fullcalendar(options, on_click=handle_click)

