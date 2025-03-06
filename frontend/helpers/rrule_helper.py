# -*- coding: UTF-8 -*-
from dateutil.rrule import rrule, rrulestr, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from helpers.date_helpers import str_to_datetime
from helpers.logging import logger
import traceback

freq_map = {
    DAILY: 'DAILY',
    WEEKLY: 'WEEKLY', 
    MONTHLY: 'MONTHLY',
    YEARLY: 'YEARLY'
}

reverse_freq_map = {
    'DAILY': DAILY,
    'WEEKLY': WEEKLY,
    'MONTHLY': MONTHLY,
    'YEARLY': YEARLY,
    None : WEEKLY
}
month_index_map = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}
weekday_map = {
    'MO': MO, 'TU': TU, 'WE': WE, 
    'TH': TH, 'FR': FR, 'SA': SA, 'SU': SU
}

weekday_index_map = {
    0: 'MO', 1: 'TU', 2: 'WE',
    3: 'TH', 4: 'FR', 5: 'SA', 6: 'SU'
}

def parse_rrule(rrule_str):
    if not rrule_str:
        return None, 1, [], [], None, None

    try:
        # Extract only RRULE part if DTSTART is present
        if '\n' in rrule_str:
            rrule_parts = rrule_str.split('\n')
            dtstart = rrule_parts[0]  # Keep DTSTART for debugging
            for part in rrule_parts:
                if part.startswith('RRULE:'):
                    rrule_str = part
                    break
        
        if not rrule_str.startswith('RRULE:'):
            rrule_str = f'RRULE:{rrule_str}'

        rule = rrulestr(rrule_str)

        freq = freq_map.get(rule._freq)
        interval = getattr(rule, '_interval', 1)
        days = [weekday_index_map[day] for day in rule._byweekday] if hasattr(rule, '_byweekday') and rule._byweekday is not None else []
        months = [month_index_map[month] for month in rule._bymonth] if hasattr(rule,'_bymonth') and rule._bymonth is not None else []
        until = getattr(rule, '_until', None)
        count = getattr(rule, '_count', None)

        return freq, interval, days, months, until, count

    except Exception as e:
        logger.debug(f"Error parsing rrule: {str(e)}")
        logger.debug(f"Input rrule string: {rrule_str}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return None, 1, [], None, None

def build_rrule_string(result, event_start, event_end=None):
    if isinstance(event_start, str):
        event_start = str_to_datetime(result['event_start_date'], result['event_start_time'])
    if event_end and isinstance(event_end, str):
        event_end = str_to_datetime(result['event_end_date'], result['event_end_time'])
    
    rule_kwargs = {
        'freq': freq_map[result['recurrence_freq']],
        'interval': int(result['recurrence_interval']),
        'dtstart': event_start
    }
    
    if result['recurrence_number']:
        rule_kwargs['count'] = int(result['recurrence_number'])

    if result['recurrence_days']:
        rule_kwargs['byweekday'] = [weekday_map[day] for day in result['recurrence_days']]

    if result['recurrence_months']:
        rule_kwargs['bymonth'] = [month_index_map[month] for month in result['recurrence_months']]
    
    if event_end and not result['recurrence_number']:
        rule_kwargs['until'] = event_end
        
    rule = rrule(**rule_kwargs)
    return str(rule)
