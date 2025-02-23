# -*- coding: UTF-8 -*-
from dateutil.rrule import rrule, rrulestr, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from helpers.date_helpers import str_to_datetime


def parse_rrule(rrule_str):
    if not rrule_str:
        return None, 1, [], None, None

    try:
        # Parse the RRULE directly using dateutil
        rule = rrulestr(rrule_str)
        
        # Map frequencies to string representations
        freq_map = {
            DAILY: 'DAILY',
            WEEKLY: 'WEEKLY', 
            MONTHLY: 'MONTHLY',
            YEARLY: 'YEARLY'
        }
        
        # Map weekdays to string representations
        weekday_map = {
            MO: 'MO', TU: 'TU', WE: 'WE',
            TH: 'TH', FR: 'FR', SA: 'SA', SU: 'SU'
        }
        
        freq = freq_map.get(rule._freq, 'WEEKLY')
        interval = rule._interval
        days = [weekday_map[day] for day in rule._byweekday] if rule._byweekday else []
        until = rule._until if hasattr(rule, '_until') else None
        count = int(rule._count) if hasattr(rule, '_count') else None

        return freq, interval, days, until, count

    except Exception as e:
        print(f"Error parsing rrule: {e}")
        return 'WEEKLY', 1, [], None, None

def build_rrule_string(result, event_start, event_end=None):
    # Convert string dates to datetime objects
    if isinstance(event_start, str):
        event_start = str_to_datetime(result['event_start_date'], result['event_start_time'])
    if event_end and isinstance(event_end, str):
        event_end = str_to_datetime(result['event_end_date'], result['event_end_time'])

    freq_map = {
        'DAILY': DAILY,
        'WEEKLY': WEEKLY,
        'MONTHLY': MONTHLY,
        'YEARLY': YEARLY,
        None: WEEKLY  # Default to WEEKLY if frequency is None
    }
    
    weekday_map = {
        'MO': MO, 'TU': TU, 'WE': WE, 
        'TH': TH, 'FR': FR, 'SA': SA, 'SU': SU
    }
    
    rule_kwargs = {
        'freq': freq_map[result['recurrence_freq']],
        'interval': int(result['recurrence_interval']),
        'dtstart': event_start
    }
    
    if result['recurrence_number']:
        rule_kwargs['count'] = int(result['recurrence_number'])

    if result['recurrence_days']:
        rule_kwargs['byweekday'] = [weekday_map[day] for day in result['recurrence_days']]
    
    if event_end and not result['recurrence_number']:
        rule_kwargs['until'] = event_end
        
    rule = rrule(**rule_kwargs)
    return str(rule)

