# -*- coding: UTF-8 -*-
from datetime import datetime, time, date
import os
import pytz
from babel.dates import format_datetime, get_date_format, get_time_format
from babel import Locale

TZ = pytz.timezone(os.environ.get('TZ', 'UTC'))
LOCALE = os.environ.get('LOCALE_LANGUAGE', 'en_US')
locale = Locale(LOCALE)

# Obtenir le format de date
date_format = 'dd/MM/yyyy' #str(get_date_format(format='long', locale=locale).pattern)

# Obtenir le format de l'heure
time_format = 'HH:MM' #str(get_time_format(format='medium', locale=locale).pattern)

# Combiner les deux pour un format datetime
datetime_format = f"{date_format} {time_format}"

def str_to_datetime(date_str, time_str):
    if isinstance(date_str, str):
        date_part = datetime.strptime(date_str, '%d/%m/%Y').date()
    elif isinstance(date_str, date):
        date_part = date_str
    
    if isinstance(time_str, str):
        # Utiliser le format 24 heures
        try:
            time_part = datetime.strptime(time_str, '%H:%M:%S').time()
        except ValueError:
            time_part = datetime.strptime(time_str, '%H:%M').time()
    elif isinstance(time_str, time):
        time_part = time_str
    else:
        raise ValueError("time_str doit être une chaîne ou un objet time")
    
    naive_dt = datetime.combine(date_part, time_part)
    return TZ.localize(naive_dt)

def datetime_to_str(dt):
    if not dt:
        return ''
    if isinstance(dt, str):
        if not dt:
            return ''
        dt = parse_iso_datetime(dt)
    return format_datetime(dt, format=f"{date_format} {time_format}", locale=LOCALE, tzinfo=TZ)

def parse_iso_datetime(iso_str):
    formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M','%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%fZ']
    for fmt in formats:
        try:
            naive_dt = datetime.strptime(iso_str, fmt)
            return TZ.localize(naive_dt)
        except ValueError:
            continue
    raise ValueError(f"time data '{iso_str}' does not match any supported format")

def datetime_to_iso_string(dt):
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, '%d/%m/%Y %H:%M')
        except ValueError:
            try:
                dt = datetime.fromisoformat(dt)
            except ValueError:
                raise ValueError(f"Format de date non pris en charge : {dt}")
    elif not isinstance(dt, datetime):
        raise ValueError(f"Type d'entrée non pris en charge : {type(dt)}")

    return dt.strftime('%Y-%m-%dT%H:%M:%S')

def datetime_to_date_to_str(dt):
    if not dt:
        return ''
    if isinstance(dt, str):
        if not dt:
            return ''
        dt = parse_iso_datetime(dt)
    return format_datetime(dt, format=date_format, locale=LOCALE, tzinfo=TZ)

def datetime_to_time_str(dt):
    if not dt:
        return ''
    if isinstance(dt, str):
        if not dt:
            return ''
        dt = parse_iso_datetime(dt)
    return format_datetime(dt, format='HH:mm', locale=LOCALE, tzinfo=TZ)