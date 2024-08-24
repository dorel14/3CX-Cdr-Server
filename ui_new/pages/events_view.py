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

class Event_Dialog(ui.dialog):
    def __init__(self, title:str, startdate:str, enddate:str, starthour:str, endhour:str,all_day:bool, impact:str, description:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Event'
        self.auto_close = False
        self.close_button = True
        with self, ui.card():
            data={}
            ui.label('Add Event')
            ui.input(label='Event title', placeholder='Event Title', value=title).on_value_change(lambda e: data.update({'event_title': e.value}))
            checkbox = ui.checkbox('All Day', value=False).on_value_change(lambda e: data.update({'event_title': e.value}))
            with ui.grid(columns=2):
                with ui.column():
                    ui.label('Start date')    
                    with ui.input(label='Start Date', value=startdate).on_value_change(lambda e: data.update({'event_start_date': e.value})) as date:
                        with ui.menu().props('no-parent-event') as datemenu:
                            with ui.date(value=today).bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=datemenu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
                with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                    ui.label('Start time')
                    #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                    with ui.input(label='Start Time', value=starthour).on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time(value=nowhour).bind_value(time):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with time.add_slot('append'):
                            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
                with ui.column():
                    ui.label('End date')    
                    with ui.input(label='End Date', value=enddate).on_value_change(lambda e: data.update({'event_end_date': e.value})) as date:
                        with ui.menu().props('no-parent-event') as datemenu:
                            with ui.date(value=today).bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=datemenu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
                with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                    ui.label('End time')
                    #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                    with ui.input(label='End Time', value=endhour).on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time(value=nowhour).bind_value(time):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with time.add_slot('append'):
                            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            
            ui.label('Impact of event')
            ui.select(options=impact_levels, value=impact).on_value_change(lambda e: data.update({'event_impact': e.value})).classes('w-full')
            ui.textarea('Event Description', placeholder='Event description', value=description).on_value_change(lambda e: data.update({'event_description': e.value})).classes('w-full')
            with ui.row():
                ui.button('Save Event', on_click=lambda: self.submit(data), icon='save').classes('text-xs')
                ui.button('Cancel', icon='close', on_click=self.close).classes('text-xs')  
        

async def Event_Dialog_open():
    result = await Event_Dialog(title='', startdate=today, starthour=nowhour, enddate=today, endhour=nowhour, impact='', description='', all_day=False)
    ui.notify(f'Event added: {result}')

async def handle_click(event: events.GenericEventArguments):
    if 'info' in event.args:
        if 'event' in event.args['info']:
            print(event.args['info']['event'])         
            result = await Event_Dialog(title=event.args['info']['event']['title'],
                            startdate=datetime.strptime(event.args['info']['event']['start'],"%Y-%m-%dT%H:%M:%S").strftime('%d-%m-%Y'),
                            starthour=datetime.strptime(event.args['info']['event']['start'],"%Y-%m-%dT%H:%M:%S").strftime('%H:%M'),
                            enddate=datetime.strptime(event.args['info']['event']['end'], "%Y-%m-%dT%H:%M:%S").strftime('%d-%m-%Y') if 'end' in  event.args['info']['event'] else '',
                            endhour=datetime.strptime(event.args['info']['event']['end'],"%Y-%m-%dT%H:%M:%S").strftime('%H:%M') if 'end' in event.args['info']['event'] else '',
                            impact=event.args['info']['event']['extendedProps']['impact'],
                            description=event.args['info']['event']['extendedProps']['description'] ,
                            all_day=event.args['info']['event']['allDay'])
            if result:
                ui.notify(f'Event updated: {result}')
            else:
                ui.notify(f'Event deleted {result}')
        else: 
            ui.notify(f'date: {event.args['info']['date']}')


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

def add_event_to_db(data):
    url = f'{api_base_url}/v1/extra_events'
    if data['event_all_day'] :
        event_start = datetime.combine(datetime.strptime(data['event_start_date'], "%Y-%m-%d"),mintime).strftime("%Y-%m-%d %H:%M:%S")
        event_end = datetime.combine(datetime.strptime(data['event_start_date'], "%Y-%m-%d"),maxtime).strftime("%Y-%m-%d %H:%M:%S")
    else:
        event_start = datetime.combine(datetime.strptime(data['event_start_date'], "%Y-%m-%d"),
                                        datetime.strptime(data['event_start_time'], "%H:%M").time())
        event_end = datetime.combine(datetime.strptime(data['event_end_date'], "%Y-%m-%d"),
                                    data['event_end_time']).strftime("%Y-%m-%d %H:%M:%S") if data['event_end_date'] else None
    e={
        'event_title': data['event_title'],
        'event_start': event_start,
        'event_end': event_end,
        'event_description': data['event_description'],
        'event_impact': data['event_impact'],
    }
    j=json.dumps(e, default=str)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, headers=headers, data=j)
    if response.status_code == 200:
        ui.notify('Event added successfully!')
        create_calendar.refresh()
    else:
        ui.notify('Failed to add event')

@ui.refreshable
def create_calendar():
    options = {
        'locale': os.environ.get('LOCALE_LANGUAGE').split('_')[0],
        'initialView': 'dayGridMonth',
        'headerToolbar': {'left': 'today', 'center':'title','right': 'multiMonthYear, dayGridMonth, timeGridWeek, timeGridDay, listWeek'},
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
    ui.button('Add Event', on_click=Event_Dialog_open).classes('text-xs')



