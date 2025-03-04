# -*- coding: UTF-8 -*-
import holidays


def get_holidays(year, country='US'):
    holidays_list = holidays.country_holidays(years=year, country=country)
    calendar_events = []
    
    for date, name in holidays_list.items():
        event = {
            'title': name,
            'start': date.strftime('%Y-%m-%d'),
            'end': date.strftime('%Y-%m-%d'),
            'allDay': True,
            'display': 'background',
            'color': '#e6f3ff',  # Light blue background
            'classNames': ['holiday-event']
        }
        calendar_events.append(event)
    
    return calendar_events