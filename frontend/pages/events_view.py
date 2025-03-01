# -*- coding: UTF-8 -*-

from fullcalendar.FullCalendar import FullCalendar as fullcalendar
from nicegui import ui, APIRouter, events
from dateutil.rrule import rrule
from .generals import theme
import requests
import json
import websockets
import asyncio
import os
from datetime import datetime, time
from babel.dates import get_period_names, get_day_names
from helpers.date_helpers import str_to_datetime,\
    datetime_to_str,\
    parse_iso_datetime, \
    datetime_to_date_to_str,\
    datetime_to_time_str,\
    datetime_to_iso_string
from helpers.rrule_helper import parse_rrule, build_rrule_string
from helpers.rrule_helper import freq_map, weekday_map, reverse_freq_map

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

def get_locale_language():
    return os.environ.get('LOCALE_LANGUAGE', 'en').split('_')[0]

def get_recurrence_options(locale):
    period_names = get_period_names(width='wide', context='stand-alone', locale=locale)
    return {
        'DAILY': period_names.get('day', 'Daily'),
        'WEEKLY': period_names.get('week', 'Weekly'),
        'MONTHLY': period_names.get('month', 'Monthly'), 
        'YEARLY': period_names.get('year', 'Yearly')
    }

def get_weekday_options(locale):
    days = get_day_names(width='wide', locale=locale)
    return {
        days.get(0, 'Monday').capitalize(): 'MO',
        days.get(1, 'Tuesday').capitalize(): 'TU',
        days.get(2, 'Wednesday').capitalize(): 'WE',
        days.get(3, 'Thursday').capitalize(): 'TH',
        days.get(4, 'Friday').capitalize(): 'FR',
        days.get(5, 'Saturday').capitalize(): 'SA',
        days.get(6, 'Sunday').capitalize(): 'SU'
    }
def get_months_options(locale):
    months = get_period_names(width='wide', context='stand-alone', locale=locale)
    return {
        months.get('january', 'January'): 'JAN',
        months.get('february', 'February'): 'FEB',
        months.get('march', 'March'): 'MAR',
        months.get('april', 'April'): 'APR',
        months.get('may', 'May'): 'MAY',
        months.get('june', 'June'): 'JUN',
        months.get('july', 'July'): 'JUL',
        months.get('august', 'August'): 'AUG',
        months.get('september', 'September'): 'SEP',
        months.get('october', 'October'): 'OCT',
        months.get('november', 'November'): 'NOV',
        months.get('december', 'December'): 'DEC'
    }
    
# Add WebSocket event handler
async def handle_queue_websocket():
    uri = f"{api_base_url.replace('http', 'ws')}/ws"
    print(f"Attempting WebSocket connection to: {uri}")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("WebSocket connection established")
                while True:
                    message = await websocket.recv()
                    print(f"Received WebSocket message: {message}")
                    data = json.loads(message)
                    action = data.get('action')
                    if action == 'create':
                        print(f"Creating event with id: {data['event']['id']}")
                        create_calendar.refresh()
                    elif action == 'update':
                        print(f"Updating event with id: {data['event']['id']}")
                        create_calendar.refresh()
                    elif action == 'delete':
                        print(f"Deleting event with id: {data['event']['id']}")
                        create_calendar.refresh()
                    else:
                        print(f"Unknown action: {action}")
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket error: {e}, attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

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

def get_event_types():
    url = f'{api_base_url}/v1/event_types'
    response = requests.get(url)
    if response.status_code == 200:
        return {event_type['id']: event_type['name'] for event_type in response.json()}
    return {}

def get_events():
    url = f'{api_base_url}/v1/extra_events'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        events = []
        for event in data:
            print(event)
            freq, interval, days, months, until, count = parse_rrule(event['recurrence_rule'])
            event_data = {
                'id': event['id'],
                'title': event['event_title'],
                'start': event['event_start'],
                'end': event['event_end'],
                'description': event['event_description'],
                'impact': impact_levels[event['event_impact']],
                'color': impact_colors[event['event_impact']],
                'allDay': event['all_day'],
                'recurrence_freq': freq,
                'recurrence_interval': interval,
                'recurrence_days': days,
                'recurrence_months': months,
                'recurrence_until': until,
                'recurrence_count': count,
                'exdate': event['exdate']
            }
            if event['recurrence_rule']:
                event_data['rrule'] = event['recurrence_rule']
            events.append(event_data)        
        return events
    return []

async def remove_queue_from_event(event_id: str, queue_id: int, dialog_instance):
    #print(f'remove_queue_from_event: {event_id}, {queue_id}')
    url = f'{api_base_url}/v1/extra_events/{event_id}/queue/{queue_id}'
    response = requests.delete(url)
    if response.status_code == 200:
        ui.notify('Queue removed from event', type='positive')
        #dialog_instance.close()
        event_response = requests.get(f'{api_base_url}/v1/extra_events/{event_id}')
        if event_response.status_code == 200:
            event_data = event_response.json()
            dialog_instance.queues = event_data['queueslist']
            dialog_instance.extensions = event_data['extensionslist']
            dialog_instance.update()     
        #create_calendar.refresh()
    else:
        ui.notify('Failed to remove queue', type='negative')

async def remove_extension_from_event(event_id: str, extension_id: int, dialog_instance):
    #print('remove extension from event')
    url = f'{api_base_url}/v1/extra_events/{event_id}/extension/{extension_id}'
    response = requests.delete(url)
    if response.status_code == 200:
        ui.notify('Extension removed from event', type='positive')
        #dialog_instance.close()
        event_response = requests.get(f'{api_base_url}/v1/extra_events/{event_id}')
        if event_response.status_code == 200:
            event_data = event_response.json()            
            dialog_instance.queues = event_data['queueslist']
            dialog_instance.extensions = event_data['extensionslist']
            dialog_instance.update()
            
        #create_calendar.refresh()
    else:
        ui.notify('Failed to remove extension', type='negative')

class Event_Dialog(ui.dialog):
    def __init__(self, id:str ,title:str, start:datetime, end:datetime, all_day:bool, impact:str, description:str, extensions:list=None, queues:list=None, eventtypes:list=None,recurrence_rule=None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Event'
        self.auto_close = False
        self.close_button = True
        selected_language = get_locale_language()
        
        freq, interval, days, months,until, count = parse_rrule(recurrence_rule)
        
        data={
            'id': id,
            'event_title': title if title else '',
            'event_allday':all_day,
            'event_start_date':datetime_to_date_to_str(start),
            'event_start_time':datetime_to_time_str(start),
            'event_end_date':datetime_to_date_to_str(end),
            'event_end_time':datetime_to_time_str(end),
            'event_impact':impact if impact else '0',
            'eventtypeslist': eventtypes if eventtypes else [],
            'event_description':description if description else '',
            'extensionslist': extensions if extensions else [],
            'queueslist': queues if queues else [],
            'recurrence_enabled': bool(recurrence_rule),
            'recurrence_rule': recurrence_rule,
            'recurrence_freq': freq,
            'recurrence_interval': interval,
            'recurrence_days': days,
            'recurrence_months' : months,
            'recurrence_number': count,
        }

        def update_end_date(count):
            if data['recurrence_enabled'] and count:
                start_date = str_to_datetime(data['event_start_date'], data['event_start_time'])
                rule_kwargs = {
                    'freq': freq_map[data['recurrence_freq']],
                    'interval': int(data['recurrence_interval']),
                    'dtstart': start_date,
                    'count': int(count)
                }
                if data['recurrence_days']:
                    rule_kwargs['byweekday'] = [weekday_map[day] for day in data['recurrence_days']]
        
                # Generate all occurrences and take the last one
                rule = rrule(**rule_kwargs)
                dates = list(rule)
                last_date = dates[-1]
    
                # Update end date/time fields
                data.update({
                    'event_end_date': datetime_to_date_to_str(last_date),
                    'event_end_time': datetime_to_time_str(last_date)
                })
                end_date_input.value = data['event_end_date']
                end_time_input.value = data['event_end_time']

        with self, ui.card():
            recurrence_options = get_recurrence_options(selected_language)
            weekday_options = get_weekday_options(selected_language)
            months_options = get_months_options(selected_language)

            ui.label('Add Event')
            ui.input(label='id', value=data['id']).props('readonly').classes('hidden')
            ui.input(label='Event title', placeholder='Event Title', value=data['event_title']).on_value_change(lambda e: data.update({'event_title': e.value}))
            with ui.row():              
                checkbox = ui.switch('All Day', value=data['event_allday']  if all_day else False ).on_value_change(lambda e: data.update({'event_allday': e.value}))
                ui.switch('Enable Recurrence', value=data['recurrence_enabled']).on_value_change(lambda e: data.update({'recurrence_enabled': e.value}))

            with ui.column().bind_visibility_from(data, 'recurrence_enabled', value=True):
                with ui.row():
                    ui.select(options=recurrence_options, value=data['recurrence_freq']).on_value_change(lambda e: (data.update({'recurrence_freq': e.value},
                                                                                                                                update_end_date(e.value))
                                                                                                                                ))
                    ui.number(label='Interval', value=data['recurrence_interval'], min=1).on_value_change(lambda e: (data.update({'recurrence_interval': e.value}),
                                                                                                                    update_end_date(e.value)))
                    ui.number('Number of occurrences', value=data['recurrence_number'], precision=0).on_value_change(
                        lambda e: (
                            data.update({'recurrence_number': e.value}),
                            update_end_date(e.value)))                    
                with ui.row():
                    for day, code in weekday_options.items():
                        ui.checkbox(day, value=code in data['recurrence_days']).on_value_change(lambda e, code=code: data['recurrence_days'].append(code) if e.value else data['recurrence_days'].remove(code))
                with ui.row():
                    for month, code in months_options.items():
                        ui.checkbox(month, value=code in data['recurrence_months']).on_value_change(lambda e, code=code: data['recurrence_months'].append(code) if e.value else data['recurrence_months'].remove(code))
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
                    with ui.input(label='Start Time', value=data['event_start_time']).on_value_change(lambda e: data.update({'event_start_time': e.value})) as time:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time(value=data['event_start_time']).bind_value(time):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with time.add_slot('append'):
                            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
                with ui.column():
                    ui.label('End date')    
                    end_date_input = ui.input(label='End Date', value=data['event_end_date']).on_value_change(lambda e: data.update({'event_end_date': e.value}))
                    with ui.menu().props('no-parent-event') as datemenu:
                        with ui.date(value=data['event_end_date'], mask=date_format).bind_value(end_date_input):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=datemenu.close).props('flat')
                    with end_date_input.add_slot('append'):
                        ui.icon('edit_calendar').on('click', datemenu.open).classes('cursor-pointer')
                with ui.column().bind_visibility_from(checkbox,'value', value=False): 
                    ui.label('End time')
                    end_time_input = ui.input(label='End Time', value=data['event_end_time']).on_value_change(lambda e: data.update({'event_end_time': e.value}))
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.time(value=data['event_end_time']).bind_value(end_time_input):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with end_time_input.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')

            ui.label('Impact of event')
            ui.select(options=impact_levels, value=data['event_impact']).on_value_change(lambda e: data.update({'event_impact': e.value})).classes('w-full')
            ui.textarea('Event Description', placeholder='Event description', value=data['event_description']).on_value_change(lambda e: data.update({'event_description': e.value})).classes('w-full')
            ui.label('Type of Event')
            event_types_options = get_event_types()
            available_event_types = {k:v for k,v in get_event_types().items() if not any(q['id'] == k for q in data['eventtypeslist'])}
            ui.select(options=available_event_types, multiple=True
                    ).on_value_change(lambda e: data.update({'eventtypeslist': [{'id': event_type_id} for event_type_id in e.value]}))
            with ui.row():
                for event_type in data['eventtypeslist']:
                        ui.chip(text=f"{event_types_options.get(event_type['id'], '')}",
                                removable=True,
                                color=event_type['color'],
                        ).on('remove',
                            lambda e: data.update({'eventtypeslist': [q for q in data['eventtypeslist'] if q['id'] != event_type['id']]}))
            ui.label('Extensions')
            extensions_options = get_extensions()
            available_extensions = {k:v for k,v in get_extensions().items() if not any(q['id'] == k for q in data['extensionslist'])}
            ui.select(options=available_extensions, multiple=True
                    ).on_value_change(lambda e: data.update({'extensionslist': [{'id': ext_id} for ext_id in e.value]}))

            with ui.row():
                for ext in data['extensionslist']:
                        ui.chip(text=f"{extensions_options.get(ext['id'], '')}",
                                removable=True,
                                color='white',
                                ).on(
                                    'remove',
                                    lambda e, ext_id=ext['id']: remove_extension_from_event(data['id'], ext_id, self)
                                ).classes('text-xs')
            ui.label('Queues')
            queues_options = get_queues()
            available_queues = {k:v for k,v in get_queues().items() if not any(q['id'] == k for q in data['queueslist'])}
            ui.select(options=available_queues,  multiple=True
                    ).on_value_change(lambda e: data.update({'queueslist': [{'id': queue_id} for queue_id in e.value]}))
            
            with ui.row():
                for queue in data['queueslist']:
                        ui.chip(text=f"{queues_options.get(queue['id'], '')}",
                        removable=True,
                        color='white',
                        ).on(
                            'remove',
                            lambda e, queue_id=queue['id']: remove_queue_from_event(data['id'], queue_id, self)
                        ).classes('text-xs')

            with ui.row():
                ui.button('Save Event', on_click=lambda: self.submit(data), icon='save').classes('text-xs')
                ui.button('Delete Event', on_click=lambda: delete_event(data['id'], data),icon='delete').classes('text-xs')
                ui.button('Cancel', icon='close', on_click=self.close).classes('text-xs')

            # Calculate end date for existing recurring events
            if recurrence_rule and count:
                update_end_date(count)
        

async def Event_Dialog_open():
    print('Event_Dialog_open')
    result = await Event_Dialog(id='', title='', start=today, end=today, impact='0', description='', all_day=False, extensions=[], queues=[], eventtypes=[], recurrence_rule=None)
    if result:
        print(result)
        add_event_to_db(result)
    ui.notify(f'Event added: {result}')

async def handle_dateclick(event: events.GenericEventArguments):
    event_info = event.args['info']
    result = await Event_Dialog(
        id='',
        title='',
        start=parse_iso_datetime(event_info['date']),
        end=parse_iso_datetime(event_info['date']),
        impact='0',
        description='',
        all_day=False,
        extensions=[],
        queues=[],
        eventtypes=[],
        recurrence_rule=None,
        exdate=None
        )
    if result:
        print(f'Dateclick: {result}')
        add_event_to_db(result)
        #ui.notify('Event added', type='positive')


async def handle_eventclick(event: events.GenericEventArguments):
    if 'info' in event.args and 'event' in event.args['info']:        
        event_info = {
            'id': event.args['info']['event']['id'],
            'title': event.args['info']['event'].get('title', ''),
            'start': event.args['info']['event']['start'],
            'end': event.args['info']['event'].get('end', event.args['info']['event']['start']),
            'allDay': event.args['info']['event']['allDay'],
            'extendedProps': event.args['info']['event']['extendedProps'],
            'rrule': event.args['info']['event'].get('rrule', None),
            'exdate': event.args['info']['event'].get('exdate', None),
        }

        # Get full event details from API
        url = f'{api_base_url}/v1/extra_events/{event_info["id"]}'
        response = requests.get(url)
        if response.status_code == 200:
            full_event = response.json()
            
            result = await Event_Dialog(
                id=event_info['id'],
                title=event_info['title'],
                start=parse_iso_datetime(event_info['start']),
                end=parse_iso_datetime(event_info['end']),
                impact=next(key for key, value in impact_levels.items() if value == event_info['extendedProps']['impact']),
                description=full_event['event_description'],
                all_day=event_info['allDay'],
                eventtypes=full_event.get('eventtypeslist', []),
                extensions=full_event.get('extensionslist', []),
                queues=full_event.get('queueslist', []),
                recurrence_rule=full_event.get('recurrence_rule', None),
                exdate=full_event.get('exdate', None)
            )
        if result:
            print(f"result: {result}")
            if result['event_allday']:
                event_start = datetime_to_str(str_to_datetime(result['event_start_date'], str(mintime)))
                event_end = datetime_to_str(str_to_datetime(result['event_end_date'], str(maxtime)))
            else:
                event_start = datetime_to_str(str_to_datetime(result['event_start_date'], result['event_start_time']))
                event_end = datetime_to_str(str_to_datetime(result['event_end_date'], result['event_end_time']))

            extensionslist = ([{'id': ext_id} for ext_id in result['extensionslist']]
                                if result['extensionslist'] and not isinstance(result['extensionslist'][0], dict)
                                else result['extensionslist'])

            queueslist = ([{'id': queue_id} for queue_id in result['queueslist']]
                            if result['queueslist'] and not isinstance(result['queueslist'][0], dict)
                            else [{'id': queue['id']} for queue in result['queueslist']])

            eventtypeslist = ([{'id': event_type_id} for event_type_id in result['eventtypeslist']]
                                if result['eventtypeslist'] and not isinstance(result['eventtypeslist'][0], dict)
                                else result['eventtypeslist'])
            # Build recurrence rule if enabled
            rrule_str = None
            if result.get('recurrence_enabled'):
                rrule_str = build_rrule_string(result, event_start, event_end)

            e = {
                'event_title': result['event_title'],
                'event_start': datetime_to_iso_string(event_start),
                'event_end': datetime_to_iso_string(event_end),
                'event_description': result['event_description'],
                'event_impact': result['event_impact'],
                'all_day': result['event_allday'],
                'eventtypeslist': eventtypeslist,
                'extensionslist': extensionslist,
                'queueslist': queueslist,
                'recurrence_rule': rrule_str,
                'exdate': result['exdate'] if result['exdate'] else []
            }
            j = json.dumps(e, default=str)
            print(f'jsonupdate {j}')
            url = f'{api_base_url}/v1/extra_events'
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = requests.patch(
                url=f'{url}/{result["id"]}',
                headers=headers,
                data=j
            )
            if response.status_code == 200:
                ui.notify('Event added successfully!', type='positive')
                create_calendar.refresh()
            else:
                ui.notify('Failed to add event', type='negative')
    
async def delete_event(event_id, form_data):
    url = f'{api_base_url}/v1/extra_events/{event_id}'
    response = requests.get(url)
    if response.status_code == 200:
        event = response.json()
        if event['recurrence_rule']:
            with ui.dialog() as dialog, ui.card():
                ui.label('Delete Recurring Event')
                ui.label('Do you want to delete this occurrence or all occurrences?')
                with ui.row():
                    ui.button('This Occurrence', on_click=lambda: handle_delete(event_id, 'single', event, form_data))
                    ui.button('All Occurrences', on_click=lambda: handle_delete(event_id, 'all', event, form_data))
                    ui.button('Cancel', on_click=dialog.close)
                await dialog
        else:
            # Non-recurring event - delete directly
            response = requests.delete(url)
            if response.status_code == 200:
                ui.notify('Event deleted successfully!', type='positive')
                create_calendar.refresh()
            else:
                ui.notify('Failed to delete event', type='negative')


async def handle_delete(event_id, delete_type, event, form_data):
    url = f'{api_base_url}/v1/extra_events/{event_id}'
    if delete_type == 'single':
        # Initialize exdate as empty list if None
        exdate = event.get('exdate', []) or []
        # Use the form's displayed date instead of event start
        form_date = str_to_datetime(
            form_data['event_start_date'], form_data['event_start_time']
        ).replace(tzinfo=None)
        exdate.append(form_date)
        
        # Update event with new exdate
        update_data = {'exdate': exdate}
        response = requests.patch(
            url=url,
            headers={'Content-type': 'application/json'},
            data=json.dumps(update_data, default=str)
        )
    else:  # delete_type == 'all'
        response = requests.delete(url)
    
    if response.status_code == 200:
        ui.notify('Event deleted successfully!', type='positive')
        create_calendar.refresh()
    else:
        print(f"Failed to delete event: {response.text}")
        ui.notify('Failed to delete event', type='negative')

def add_event_to_db(data):
    if data['event_allday']:
        event_start = datetime_to_str(str_to_datetime(data['event_start_date'], str(mintime)))
        event_end = datetime_to_str(str_to_datetime(data['event_end_date'], str(maxtime)))
    else:
        event_start = datetime_to_str(str_to_datetime(data['event_start_date'], data['event_start_time']))
        event_end = datetime_to_str(str_to_datetime(data['event_end_date'], data['event_end_time']))
    rrule_str = None
    if data.get('recurrence_enabled'):
        rrule_str = build_rrule_string(data, event_start, event_end)
    
    e = {
        'event_title': data['event_title'],
        'event_start': datetime_to_iso_string(event_start),
        'event_end': datetime_to_iso_string(event_end),
        'event_description': data['event_description'],
        'event_impact': data['event_impact'],
        'all_day': data['event_allday'],
        'eventtypeslist': [],
        'extensionslist': [],
        'queueslist': [],
        'recurrence_rule': rrule_str,
        'exdate': data['exdate'] if data['exdate'] else []

    }
    if data.get('eventtypeslist'):
        if isinstance(data['eventtypeslist'][0], dict):
            e['eventtypeslist'] = [{'id': int(event_type['id'])} for event_type in data['eventtypeslist']]
        else:
            e['eventtypeslist'] = [{'id': int(event_type_id)} for event_type_id in data['eventtypeslist']]

    if data.get('extensionslist'):
        if isinstance(data['extensionslist'][0], dict):
            e['extensionslist'] = [{'id': int(ext['id'])} for ext in data['extensionslist']]
        else:
            e['extensionslist'] = [{'id': int(ext_id)} for ext_id in data['extensionslist']]

    if data.get('queueslist'):
        if isinstance(data['queueslist'][0], dict):
            e['queueslist'] = [{'id': int(queue['id'])} for queue in data['queueslist']]
        else:
            e['queueslist'] = [{'id': int(queue_id)} for queue_id in data['queueslist']]  
    

    j = json.dumps(e, default=str)
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
        'locale': get_locale_language(),
        'initialView': 'dayGridMonth',
        'headerToolbar': {'left':'prev today next', 
                        'center':'title',
                        'right': 'multiMonthYear, dayGridMonth, timeGridWeek, timeGridDay'},
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
        'selectable': True,
        'weekNumbers': True,
        'eventSources':[ 
            get_events()
            ]
        }
    fullcalendar(options, on_dateClick=handle_dateclick, on_eventClick=handle_eventclick) 



@router.page('/')
def events_view():
    asyncio.create_task(handle_queue_websocket())
    ui.page_title("3CX CDR Server app - Events")    
    with theme.frame('- Events -'):
        ui.label('')
        #message('Extensions')
    create_calendar()
    ui.button('Add Event', on_click=Event_Dialog_open).classes('text-xs')




