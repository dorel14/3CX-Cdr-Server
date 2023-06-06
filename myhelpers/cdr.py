# -*- coding: utf-8 -*-
import calendar
from datetime import datetime as dt, timedelta as td
from babel.dates import format_date
from myhelpers.logging import logger
import os
import pandas as pd
import numpy as np
from io import StringIO



def to_local_datetime(utc_dt):
    """
    convert from utc datetime to a locally aware datetime
     according to the host timezone

    :param utc_dt: utc datetime
    :return: local timezone datetime
    """
    return dt.fromtimestamp(calendar.timegm(utc_dt.timetuple()))





def parse_cdr(data):
    """Fonction permettant de splitter un CDR et de l'intégrer en BDD

    Args:
        data (String): Chaine csv séparée par des virgules

    Returns:
        _String_: Renvoi OK si insertion en BDD ok
    """
    lang = os.environ.get('LOCALE_LANGUAGE')
    print(lang)
    cdr_columns_names = [
        "historyid",
        "callid",
        "duration",
        "time_start",
        "time_answered",
        "time_end",
        "reason_terminated",
        "from_no",
        "to_no",
        "from_dn",
        "to_dn",
        "dial_no",
        "reason_changed",
        "final_number",
        "final_dn",
        "bill_code",
        "bill_rate",
        "bill_cost",
        "bill_name",
        "chain",
        "from_type",
        "to_type",
        "final_type",
        "from_dispname",
        "to_dispname",
        "final_dispname",
        "missed_queue_calls",
    ]
    types = {
        "from_no": str,
        "to_no": str,
        "from_dn": str,
        "to_dn": str,
        "dial_no": str,
        "final_number": str,
        "final_dn": str,
        "time_start": str,
        "time_answered": str,
        "time_end": str,
    }
    dates_columns = ["time_start", "time_answered", "time_end"]
    date_format = "%Y/%m/%d %H:%M:%S"
    date_format_out = "%Y/%m/%dT%H:%M:%S.078Z"

    df_cdr = pd.read_csv(
        StringIO(data),
        delimiter=",",
        header=None,
        na_values="",
        index_col=False,
        names=cdr_columns_names,
        dtype=types,
    )
    print(df_cdr)

    df_cdr_details_columns = [
        "cdr_historyid",
        "abandonned",
        "handling_time_seconds",
        "waiting_time_seconds",
        "call_date",
        "call_time",
        "call_week",
        "day_of_week"
    ]
    df_cdr_details = pd.DataFrame(columns=df_cdr_details_columns)
    df_cdr_details["cdr_historyid"] = df_cdr["historyid"]
    df_cdr_details["abandonned"] = np.where(
        (df_cdr["reason_terminated"] == "TerminatedBySrc")
        & (df_cdr["time_answered"] == ""),
        True,
        False,
    )
    df_cdr_details["handling_time_seconds"] = (
        (pd.to_datetime(df_cdr["time_end"], format=date_format)
        - pd.to_datetime(df_cdr["time_answered"], format=date_format)).dt.total_seconds()
        if not (df_cdr["time_answered"].isnull)
        else (pd.to_datetime(df_cdr["time_end"], format=date_format)
        - pd.to_datetime(df_cdr["time_start"], format=date_format)).dt.total_seconds()
    )
    df_cdr_details["waiting_time_seconds"] = (
        (pd.to_datetime(df_cdr["time_answered"], format=date_format)
        - pd.to_datetime(df_cdr["time_start"], format=date_format)).dt.total_seconds()
        if not (df_cdr["time_answered"].isnull)
        else (pd.to_datetime(df_cdr["time_end"], format=date_format)
        - pd.to_datetime(df_cdr["time_start"], format=date_format)).dt.total_seconds()
    )
    df_cdr_details["call_date"] = df_cdr["time_start"].apply(
        lambda x: dt.date(dt.strptime(x, date_format)).strftime("%d/%m/%Y")
    )
    df_cdr_details["call_time"] = df_cdr["time_start"].apply(
        lambda x: dt.time(dt.strptime(x, date_format))
    )
    df_cdr_details["call_week"] = pd.to_datetime(df_cdr["time_start"], format=date_format).dt.isocalendar().week
    df_cdr_details["day_of_week"] = df_cdr["time_start"].apply(
        lambda x: format_date(dt.strptime(x, date_format), "EEEE", locale=lang)
    )

    df_cdr_details=df_cdr_details.astype({'handling_time_seconds':int,'waiting_time_seconds':int })

  

    df_cdr["time_start"] = df_cdr["time_start"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format)).strftime(
            date_format_out
        )
    )
    df_cdr["time_answered"] = np.where(
        df_cdr["time_answered"].isnull, df_cdr["time_end"], df_cdr["time_answered"]
    )
    df_cdr["time_answered"] = df_cdr["time_answered"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format)).strftime(
            date_format_out
        )
    )
    df_cdr["time_end"] = df_cdr["time_end"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format)).strftime(
            date_format_out
        )
    )

    cdr = df_cdr.to_json(orient="records", lines=True)
    cdr_details = df_cdr_details.to_json(orient="records", lines=True)
    # print(cdr)
    # print(cdr_details)

    logger.info(cdr)
    logger.info(cdr_details)


    return cdr, cdr_details
