# -*- coding: UTF-8 -*-
from fullcalendar.FullCalendar import FullCalendar as fullcalendar
from nicegui import ui, APIRouter, events
from message import message  # noqa: F401
import theme
import requests
import json
import sys
import os
from datetime import datetime, date




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
        '3': 'High',
        '4': 'Critical',
    }
mintime = '00:00:00'
maxtime = '23:59:00'
today = date.today().strftime("%Y-%m-%d")
nowhour = datetime.now().strftime("%H:%M")


    


def handle_click(event: events.GenericEventArguments):
    if 'info' in event.args:
        if 'event' in event.args['info']:
            ui.notify(f'event: {event.args['info']['event']}')
        else: 
            ui.notify(f'event: {event.args['info']['date']}')


def get_events():
    url = f'{api_base_url}/v1/extra_events'
    response = requests.get(url)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        events = []
        for event in data:
                events.append({
                    'id': event['id'],
                    'title': event['event_title'],
                    'start': event['event_start'],
                    'end': event['event_end'],
                    'description':event['event_description'],
                    'impact':impact_levels[event['event_impact']],
                    'color': impact_colors[event['event_impact']],
                    'allDay': event['all_day'],
            }
            )
        return events
    else:
        return []

def add_event_to_db(data, dialog):
    url = f'{api_base_url}/v1/extra_events'
    e={
        'event_title': data['event_title'],
        'event_start': datetime.combine(datetime.strptime(data['event_start_date'], "%Y-%m-%d"),
                                        datetime.strptime(data['event_start_time'], "%H:%M").time()),
        'event_end': None,
        'event_description': data['event_description'],
        'event_impact': data['event_impact'],
    }
    j=json.dumps(e, default=str)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, headers=headers, data=j)
    if response.status_code == 200:
        ui.notify('Event added successfully!')
        create_calendar.refresh()
        dialog.close()
    else:
        ui.notify('Failed to add event')

@ui.refreshable
def create_calendar():
    options = {
        'locale': os.environ.get('LOCALE_LANGUAGE').split('_')[0],
        'initialView': 'dayGridMonth',
        'headerToolbar': {'left': 'today', 
                          'center':'title',
                          'right': 'multiMonthYear, dayGridMonth, timeGridWeek, timeGridDay, listWeek'
                          },
        'footerToolbar': {'right': 'prev,next'},
        'slotMinTime': mintime,
        'slotMaxTime': maxtime,
        'duration': '01:00:00',
        'allDaySlot': False,
        'timeZone': os.environ.get('TZ'),
        'height': 'auto',
        #'width': 'auto',
        'selectable': True,
        'weekNumbers': True,
        'events': get_events(),
        }
    fullcalendar(options, on_click=handle_click) 



@router.page('/')
def events_view():
    ui.page_title("3CX CDR Server app - Events")    
    with theme.frame('- Events -'):
        ui.label('')
        #message('Extensions')
    create_calendar()
    with ui.dialog() as add_event, ui.card():
        data={}
        ui.label('Add Event')
        ui.input('Event Title', placeholder='Event Title').on_value_change(lambda e: data.update({'event_title': e.value}))
        checkbox = ui.checkbox('All Day', value=False).on_value_change(lambda e: data.update({'event_title': e.value}))
        with ui.grid(columns=2):
            with ui.column():
                ui.label('Start date')    
                with ui.input('Start Date').on_value_change(lambda e: data.update({'event_start_date': e.value})) as date:
                    with ui.menu().props('no-parent-event') as datemenu:
                        with ui.date(value=today).bind_value(date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=datemenu.close).props('flat')
                    with date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
            with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                ui.label('Start time')
                #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                with ui.input('Start Time').on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.time(value=nowhour).bind_value(time):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with time.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            with ui.column():
                ui.label('End date')    
                with ui.input('End Date').on_value_change(lambda e: data.update({'event_end_date': e.value})) as date:
                    with ui.menu().props('no-parent-event') as datemenu:
                        with ui.date(value=today).bind_value(date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=datemenu.close).props('flat')
                    with date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
            with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                ui.label('End time')
                #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                with ui.input('End Time').on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.time(value=nowhour).bind_value(time):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with time.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            
        ui.label('Impact of event')
        ui.select(options=impact_levels).on_value_change(lambda e: data.update({'event_impact': e.value})).classes('w-full')
        ui.textarea('Event Description', placeholder='Event description').on_value_change(lambda e: data.update({'event_description': e.value})).classes('w-full')
        with ui.row():
            ui.button('Add Event', on_click=lambda: add_event_to_db(data,add_event), icon='add').classes('text-xs')
            ui.button('Cancel', icon='close', on_click=add_event.close).classes('text-xs')  
    ui.button('Add Event', on_click=add_event.open).classes('text-xs')



