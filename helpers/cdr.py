# -*- coding: utf-8 -*-
import calendar
from datetime import datetime

from helpers.base import DbSession, call_data_records



def to_local_datetime(utc_dt):
    """
    convert from utc datetime to a locally aware datetime
     according to the host timezone

    :param utc_dt: utc datetime
    :return: local timezone datetime
    """
    return datetime.fromtimestamp(calendar.timegm(utc_dt.timetuple()))


def parse_cdr(data):
    parsed_cdr = data.split(',')
    historyid = parsed_cdr[0]
    callid = parsed_cdr[1]
    duration = datetime.strptime(parsed_cdr[2],
                                 '%H:%M:%S').time() if parsed_cdr[2] != '' else None
    time_start = to_local_datetime(datetime.strptime(parsed_cdr[3],
                                                     '%Y/%m/%d %H:%M:%S')) if parsed_cdr[3] != '' else None

    time_answered = to_local_datetime(datetime.strptime(parsed_cdr[4],
                                                        '%Y/%m/%d %H:%M:%S')) if parsed_cdr[4] != '' else None
    time_end = to_local_datetime(datetime.strptime(parsed_cdr[5],
                                                   '%Y/%m/%d %H:%M:%S')) if parsed_cdr[5] != '' else None
    reason_terminated = parsed_cdr[6]
    from_no = parsed_cdr[7]
    to_no = parsed_cdr[8]
    from_dn = parsed_cdr[9]
    to_dn = parsed_cdr[10]
    dial_no = parsed_cdr[11]
    reason_changed = parsed_cdr[12]
    final_number = parsed_cdr[13]
    final_dn = parsed_cdr[14]
    bill_code = parsed_cdr[15]
    bill_rate = parsed_cdr[16]
    bill_cost = parsed_cdr[17]
    bill_name = parsed_cdr[18]
    chain = parsed_cdr[19]
    cdr = call_data_records(historyid=historyid,
                            callid=callid,
                            duration=duration,
                            time_start=time_start,
                            time_answered=time_answered,
                            time_end=time_end,
                            reason_terminated=reason_terminated,
                            from_no=from_no,
                            to_no=to_no,
                            from_dn=from_dn,
                            to_dn=to_dn,
                            dial_no=dial_no,
                            reason_changed=reason_changed,
                            final_number=final_number,
                            final_dn=final_dn,
                            bill_code=bill_code,
                            bill_rate=bill_rate,
                            bill_cost=bill_cost,
                            bill_name=bill_name,
                            chain=chain
                            )
    DbSession.add(cdr)
    DbSession.commit()
    return 'ok'
