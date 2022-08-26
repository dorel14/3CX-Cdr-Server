# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, timedelta
from helpers.logging import logger
from sqlmodel import Session
from helpers.base import engine
from model.tab3cxcdr import call_data_records, call_data_records_details

fr_dayofweek = {0:'Lundi', 1:'Mardi', 2:'Mercredi', 3:'Jeudi', 4:'Vendredi', 5:'Samedi', 6:'Dimanche'}
def to_local_datetime(utc_dt):
    """
    convert from utc datetime to a locally aware datetime
     according to the host timezone

    :param utc_dt: utc datetime
    :return: local timezone datetime
    """
    return datetime.fromtimestamp(calendar.timegm(utc_dt.timetuple()))


def datediff(startdate, enddate):
    """Fonction permettant de calculer le nombre de secondes entre les dates du cdr
    Args:
    startdate: date de debut au format texte '%Y/%m/%d %H:%M:%S'
    enddate: date de fin au format texte '%Y/%m/%d %H:%M:%S'
    Return: nombre de seconde entre les 2 dates / heures
    """
    datestart = to_local_datetime(datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S'))
    # logger.info(datestart)
    dateend = to_local_datetime(datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S'))
    # logger.info(dateend)
    diff = (dateend - datestart).total_seconds()
    # logger.info(diff)
    return diff


def parse_cdr(data):
    """Fonction permettant de splitter un CDR et de l'intégrer en BDD

    Args:
        data (String): Chaine csv séparée par des virgules

    Returns:
        _String_: Renvoi OK si insertion en BDD ok
    """
    parsed_cdr = data.split(',')
    logger.info(parsed_cdr)
    cdr = call_data_records(historyid=parsed_cdr[0],
                            callid=parsed_cdr[1],
                            duration=datetime.strptime(parsed_cdr[2],
                                '%H:%M:%S').time() if parsed_cdr[2] != '' else None,
                            time_start=to_local_datetime(
                                datetime.strptime(parsed_cdr[3],
                                                  '%Y/%m/%d %H:%M:%S')) if parsed_cdr[3] != '' else None,
                            time_answered=to_local_datetime(datetime.strptime(parsed_cdr[4],
                                                        '%Y/%m/%d %H:%M:%S')) if parsed_cdr[4] != '' else None,
                            time_end=to_local_datetime(datetime.strptime(parsed_cdr[5],
                                                   '%Y/%m/%d %H:%M:%S')) if parsed_cdr[5] != '' else None,
                            reason_terminated=parsed_cdr[6],
                            from_no=parsed_cdr[7],
                            to_no=parsed_cdr[8],
                            from_dn=parsed_cdr[9],
                            to_dn=parsed_cdr[10],
                            dial_no=parsed_cdr[11],
                            reason_changed=parsed_cdr[12],
                            final_number=parsed_cdr[13],
                            final_dn=parsed_cdr[14],
                            bill_code=parsed_cdr[15],
                            bill_rate=parsed_cdr[16],
                            bill_cost=parsed_cdr[17],
                            bill_name=parsed_cdr[18],
                            chain=parsed_cdr[19],
                            from_type=parsed_cdr[20],
                            to_type=parsed_cdr[21],
                            final_type=parsed_cdr[22],
                            from_dispname=parsed_cdr[23],
                            to_dispname=parsed_cdr[24],
                            final_dispname=parsed_cdr[25],
                            missed_queue_calls=parsed_cdr[26],
                            )
    setcdrdetails = call_data_records_details(cdr_historyid=parsed_cdr[0],
                                              abandonned=True if parsed_cdr[6] == 'TerminatedBySrc'
                                              and parsed_cdr[4] == '' else False,
                                              handling_time_seconds=datediff(parsed_cdr[4], parsed_cdr[5]) if parsed_cdr[4] != '' else 0,
                                              waiting_time_seconds=datediff(parsed_cdr[3], parsed_cdr[5]) if parsed_cdr[4] == '' else datediff(parsed_cdr[3], parsed_cdr[4]),
                                              call_date=datetime.date(to_local_datetime(parsed_cdr[3])),
                                              call_time=datetime.time(to_local_datetime(parsed_cdr[3])),
                                              day_of_week=fr_dayofweek[datetime.weekday(to_local_datetime(parsed_cdr[3]))]
                                              )
    logger.info(cdr)
    logger.info(setcdrdetails)
    with Session(engine) as DbSession:
        DbSession.add(cdr)
        DbSession.add(setcdrdetails)
        DbSession.commit()
    return 'ok'
