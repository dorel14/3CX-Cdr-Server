# -*- coding: UTF-8 -*-

from fullcalendar.FullCalendar import FullCalendar as fullcalendar
from nicegui import ui, APIRouter, events
from .generals import theme
import requests
import json

import os
from datetime import datetime, time

from helpers.date_helpers import str_to_datetime,\
    datetime_to_str,\
    parse_iso_datetime, \
    datetime_to_date_to_str,\
    datetime_to_time_str,\
    datetime_to_iso_string

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
mintime = time(0,0,0)
maxtime = time(23,59,59)

today = parse_iso_datetime(datetime.now().strftime("%Y/%m/%d %H:%M"))
datetimeformat = "%Y/%m/%d %H:%M"
date_format = "DD/MM/YYYY"
time_format = '%H:%M'

def get_extensions():
    url = f'{api_base_url}/v1/extensions'
    response = requests.get(url)
    if response.status_code == 200:
        return {ext['id']: ext['name'] for ext in response.json()}
    return {}

def get_queues():
    url = f'{api_base_url}/v1/queues'
    response = requests.get(url)
    if response.status_code == 200:
        return {queue['id']: queue['queuename'] for queue in response.json()}
    return {}

def get_events():
    url = f'{api_base_url}/v1/extra_events'
    response = requests.get(url)
    #print(response.json())
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
                    'extensionslist': event['extensionslist'],
                    'queueslist': event['queueslist']
            })
        return events
    else:
        return []

# async def remove_queue_from_event(event_id: str, queue_id: int, dialog_instance):
#     print(f'remove_queue_from_event: {event_id}, {queue_id}')
#     url = f'{api_base_url}/v1/extra_events/{event_id}/queue/{queue_id}'
#     response = requests.delete(url)
#     if response.status_code == 200:
#         ui.notify('Queue removed from event', type='positive')
#         dialog_instance.close()
#         event_response = requests.get(f'{api_base_url}/v1/extra_events/{event_id}')
#         if event_response.status_code == 200:
#             event_data = event_response.json()
#             dialog_instance.queues = event_data['queueslist']
#             dialog_instance.extensions = event_data['extensionslist']
#             dialog_instance.update()     
#         create_calendar.refresh()
#     else:
#         ui.notify('Failed to remove queue', type='negative')

# async def remove_extension_from_event(event_id: str, extension_id: int, dialog_instance):
#     print('remove extension from event')
#     url = f'{api_base_url}/v1/extra_events/{event_id}/extension/{extension_id}'
#     response = requests.delete(url)
#     if response.status_code == 200:
#         ui.notify('Extension removed from event', type='positive')
#         #dialog_instance.close()
#         event_response = requests.get(f'{api_base_url}/v1/extra_events/{event_id}')
#         if event_response.status_code == 200:
#             event_data = event_response.json()            
#             dialog_instance.queues = event_data['queueslist']
#             dialog_instance.extensions = event_data['extensionslist']
#             dialog_instance.update()
            
#         create_calendar.refresh()
#     else:
#         ui.notify('Failed to remove extension', type='negative')

class Event_Dialog(ui.dialog):
    def __init__(self, id:str ,title:str, start:datetime, end:datetime, all_day:bool, impact:str, description:str, extensions:list=None, queues:list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Event'
        self.auto_close = False
        self.close_button = True
        with self, ui.card():
            data={
                    'id': id,
                    'event_title': title if title else '',
                    'event_allday':all_day,
                    'event_start_date':datetime_to_date_to_str(start),
                    'event_start_time':datetime_to_time_str(start),
                    'event_end_date':datetime_to_date_to_str(end), #if all_day and datetime_to_date_to_str(end) == datetime_to_date_to_str(start) else  datetime_to_date_to_str(end),
                    'event_end_time':datetime_to_time_str(end),
                    'event_impact':impact if impact else '0',
                    'event_description':description if description else '',
                    'extensionslist': extensions if extensions else [],
                    'queueslist': queues if queues else []
                    }
            ui.label('Add Event')
            ui.input(label='id', value=data['id']).props('readonly').classes('hidden')
            ui.input(label='Event title', placeholder='Event Title', value=data['event_title']).on_value_change(lambda e: data.update({'event_title': e.value}))
            checkbox = ui.checkbox('All Day', value=data['event_allday']  if all_day else False ).on_value_change(lambda e: data.update({'event_allday': e.value}))
            with ui.grid(columns=2):
                with ui.column():
                    ui.label('Start date')    
                    with ui.input(label='Start Date', value=data['event_start_date']).on_value_change(lambda e: data.update({'event_start_date': e.value})) as date:
                        with ui.menu().props('no-parent-event') as datemenu:
                            with ui.date(value=data['event_start_date'], mask=date_format).bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=datemenu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
                with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                    ui.label('Start time')
                    #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                    with ui.input(label='Start Time', value=data['event_start_time']).on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time(value=data['event_start_time']).bind_value(time):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with time.add_slot('append'):
                            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
                with ui.column():
                    ui.label('End date')    
                    with ui.input(label='End Date', value=data['event_end_date']).on_value_change(lambda e: data.update({'event_end_date': e.value})) as date:
                        with ui.menu().props('no-parent-event') as datemenu:
                            with ui.date(value=data['event_end_date'], mask=date_format).bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=datemenu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
                with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                    ui.label('End time')
                    #ui.time(value=nowhour).on_value_change(lambda e: data.update({'event_start_time': e.value}))
                    with ui.input(label='End Time', value=data['event_end_time']).on_value_change(lambda e: data.update({'event_end_time': e.value})) as time:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time(value=data['event_end_time']).bind_value(time):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with time.add_slot('append'):
                            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            
            ui.label('Impact of event')
            ui.select(options=impact_levels, value=data['event_impact']).on_value_change(lambda e: data.update({'event_impact': e.value})).classes('w-full')
            ui.textarea('Event Description', placeholder='Event description', value=data['event_description']).on_value_change(lambda e: data.update({'event_description': e.value})).classes('w-full')
            ui.label('Extensions')
            extensions_options = get_extensions()    
            ui.select(options=extensions_options, multiple=True).on_value_change(lambda e: data.update({'extensionslist': e.value})).classes('w-full')
            print(f'data_extensions : {data['extensionslist']}')
            print(f'extensions: {extensions}')
            with ui.row():
                for ext in data['extensionslist']:
                        print(ext)
                    #with ui.grid(columns=2).classes('q-pa-sm'):
                        #ui.label(f"{extensions_options.get(ext['id'], '')}")
                        ui.button(text=f"{extensions_options.get(ext['id'], '')}",
                                icon='close',
                                #on_click=lambda e, ext_id=ext['id']: remove_extension_from_event(data['id'], ext_id, self)
                                ).classes('text-xs').props('flat rounded')
            ui.label('Queues')
            queues_options = get_queues()
            ui.select(options=queues_options,  multiple=True).on_value_change(lambda e: data.update({'queueslist': e.value})).classes('w-full')
            # After the existing Queues select            
            with ui.row():
                for queue in data['queueslist']:
                        print(queue)
                    #with ui.card().classes('q-pa-sm'):
                        #ui.label(f"{queues_options.get(queue['id'], '')}")
                        ui.button(text=f"{queues_options.get(queue['id'], '')}",
                                icon='close',
                                #on_click=lambda e, queue_id=queue['id']: remove_queue_from_event(data['id'], queue_id, self)
                                ).classes('text-xs').props('flat rounded')


            with ui.row():
                ui.button('Save Event', on_click=lambda: self.submit(data), icon='save').classes('text-xs')
                ui.button('Delete Event', on_click=lambda: delete_event(data['id']),icon='delete').classes('text-xs')
                ui.button('Cancel', icon='close', on_click=self.close).classes('text-xs')  
        

async def Event_Dialog_open():
    print('Event_Dialog_open')
    result = await Event_Dialog(id='', title='', start=today, end=today, impact='0', description='', all_day=False, extensions=[], queues=[])
    if result:
        #print(result)
        add_event_to_db(result)
    ui.notify(f'Event added: {result}')


async def handle_click(event: events.GenericEventArguments):
    if 'info' in event.args and 'event' in event.args['info']:
            #print(event.args['info'])
            event_info = event.args['info']['event']
            #ui.notify(event_info)       
            result = await Event_Dialog(
                            id=event_info['id'],   
                            title=event_info['title'] if 'title' in event_info else '',
                            start=parse_iso_datetime(event_info['start']),                          
                            end=parse_iso_datetime(event_info['end']) if 'end' in event_info else '',                            
                            impact= next(key for key, value in impact_levels.items() if value == event_info['extendedProps']['impact']),
                            description=event_info['extendedProps']['description'] ,
                            all_day=event_info['allDay'],
                            extensions=event_info['extendedProps'].get('extensionslist', []),
                            queues=event_info['extendedProps'].get('queueslist', []) 
                            )
            if result:
                print(f"result: {result}")
                if result['event_allday'] :
                    event_start = datetime_to_str(str_to_datetime(result['event_start_date'], str(mintime)))
                    event_end = datetime_to_str(str_to_datetime(result['event_end_date'], str(maxtime)))
                else:
                    event_start = datetime_to_str(str_to_datetime(result['event_start_date'], result['event_start_time']))
                    event_end = datetime_to_str(str_to_datetime(result['event_end_date'], result['event_end_time']))
                e={
                    #'event_id': result['id'],
                    'event_title': result['event_title'],
                    'event_start': datetime_to_iso_string(event_start),
                    'event_end': datetime_to_iso_string(event_end),
                    'event_description': result['event_description'],
                    'event_impact': result['event_impact'],
                    'all_day': result['event_allday'],
                    'extensionslist': [{'id': ext_id} for ext_id in result['extensionslist']],
                    'queueslist': [{'id': queue_id} for queue_id in result['queueslist']]
                    }                
                j=json.dumps(e, default=str)
                print(f'jsonupdate {j}')
                url = f'{api_base_url}/v1/extra_events'
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                response = requests.patch(
                                            url=f'{url}/{result['id']}', 
                                            headers=headers, 
                                            data=j
                                            )
                if response.status_code == 200:
                    ui.notify('Event added successfully!', type='positive')
                    create_calendar.refresh()
                else:
                    ui.notify('Failed to add event',type='negative')
    elif 'info' in event.args and 'date' in event.args['info']:
            print(event.args['info'])
            event_info = event.args['info']
            result=  await Event_Dialog(
                            id='',   
                            title='',
                            start=parse_iso_datetime(event_info['date']),                          
                            end=parse_iso_datetime(event_info['date']),                            
                            impact= '0',
                            description='',
                            all_day=False)
            if result:
                add_event_to_db(result)
                #create_calendar.refresh()
                ui.notify('Event added', type='positive')

async def delete_event(event_id):
    url = f'{api_base_url}/v1/extra_events/{event_id}'
    response = requests.delete(url)
    if response.status_code == 200:
        ui.notify('Event deleted successfully!', type='positive')
        create_calendar.refresh()
    else:
        ui.notify('Failed to delete event', type='negative')



def add_event_to_db(data):
    
    #print(f'data: {data}')
    if data['event_allday'] :
        event_start = datetime_to_str(str_to_datetime(data['event_start_date'], str(mintime)))
        event_end = datetime_to_str(str_to_datetime(data['event_end_date'], str(maxtime)))
    else:
        event_start = datetime_to_str(str_to_datetime(data['event_start_date'], data['event_start_time']))
        event_end = datetime_to_str(str_to_datetime(data['event_end_date'], data['event_end_time']))
    e={
        'event_title': data['event_title'],
        'event_start': datetime_to_iso_string(event_start),
        'event_end': datetime_to_iso_string(event_end),
        'event_description': data['event_description'],
        'event_impact': data['event_impact'],
        'all_day': data['event_allday'],
        'extensionslist': [{'id': ext_id} for ext_id in data['extensionslist']],
        'queueslist': [{'id': queue_id} for queue_id in data['queueslist']]
}
    j=json.dumps(e, default=str)
    print(f'json: {j}')
    url = f'{api_base_url}/v1/extra_events'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, headers=headers, data=j)
    if response.status_code == 200:
        ui.notify('Event added successfully!', type='positive')
        create_calendar.refresh()
    else:
        ui.notify('Failed to add event', type='negative')

@ui.refreshable
def create_calendar():
    options = {
        'locale': os.environ.get('LOCALE_LANGUAGE').split('_')[0],
        'initialView': 'dayGridMonth',
        'headerToolbar': {'left':'prev today next', 'center':'title','right': 'multiMonthYear, dayGridMonth, timeGridWeek, timeGridDay, listWeek'},
        'footerToolbar': {'right': 'prev,next'},
        'slotMinTime': mintime,
        'slotMaxTime': maxtime,
        'displayEventTime': True,
        'defaultTimedEventDuration': '01:00:00',
        'forceEventDuration': True,
        'duration': '01:00:00',
        'defaultAllDayEventDuration': {'days':1},
        'nextDayThreshold': '23:59:59',
        'allDaySlot': True,
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



