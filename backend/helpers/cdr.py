# -*- coding: utf-8 -*-
import os
import json
import pytz
from babel.dates import format_date
from urllib.parse import quote
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime as dt
import traceback
import requests
from requests.exceptions import HTTPError
from .logging import logger
from ..config.settings import CONFIG
import sys
sys.path.append(os.path.abspath("."))


def to_local_datetime(dt_obj):
    """
    convert from utc datetime to a locally aware datetime
    according to the host timezone

    :param utc_dt: utc datetime
    :return: local timezone datetime
    """
    tz = pytz.timezone(os.environ.get("TZ"))
    return dt_obj.astimezone(tz=tz)


def parse_cdr(data,filename=''):
    """Fonction permettant de splitter un CDR et de l'intégrer en BDD

    Args:
        data (String): Chaine csv séparée par des virgules
        filename (String) : Chaine indiquant le nom du fichier dont est extrait le CDR

    Returns:
        _String_: Renvoi 2 Json :
            - 1 avec le call data record
            - 1 avec des valeurs calculées à partir du précédent
    """
    lang = os.environ.get("LOCALE_LANGUAGE")
    logger.info(lang)
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
        "bill_code": str,
        "bill_name": str,
        "chain": str,
        "time_start": str,
        "time_answered": str,
        "time_end": str,
        "missed_queue_calls":str,
        "from_type": str,
        "to_type" : str,
        "final_type": str,
        "from_dispname": str,
        "to_dispname": str,
        "final_dispname": str
    }

    dates_columns = ["time_start", "time_answered", "time_end"]
    date_format = "%Y/%m/%d %H:%M:%S"
    date_format_out = "%Y/%m/%dT%H:%M:%S.078Z"

    df_cdr = pd.read_csv(
        StringIO(data),
        delimiter=",",
        header=None,
        na_values=None,
        index_col=False,
        names=cdr_columns_names,
        dtype=types,
    )
    logger.info(df_cdr)    

    df_cdr_details_columns = [
        "cdr_historyid",
        "abandonned",
        "handling_time_seconds",
        "waiting_time_seconds",
        "call_date",
        "call_time",
        "call_week",
        "day_of_week",
        "filename"
    ]
    df_cdr_details = pd.DataFrame(columns=df_cdr_details_columns)
    df_cdr_details["cdr_historyid"] = df_cdr["historyid"]

    df_cdr_details["abandonned"] = np.where((df_cdr["reason_terminated"].str.contains("TerminatedBySrc"))
                                            & (df_cdr["final_dn"].isna() |df_cdr["final_dn"].isnull() )
                                            & (df_cdr["from_no"].str.contains("Ext.*", regex=True) is False),
                                            True,
                                            False)

    df_cdr_details["handling_time_seconds"] = (
        (
            pd.to_datetime(df_cdr["time_end"], format=date_format)
            - pd.to_datetime(df_cdr["time_answered"], format=date_format).fillna(df_cdr["time_start"])
        ).dt.total_seconds()
    )
    df_cdr_details["waiting_time_seconds"] = (
        (
            pd.to_datetime(df_cdr["time_answered"], format=date_format).fillna(df_cdr["time_end"])
            - pd.to_datetime(df_cdr["time_start"], format=date_format)
        ).dt.total_seconds()
        )

    df_cdr_details["call_date"] = df_cdr["time_start"].apply(
        lambda x: dt.date(dt.strptime(x, date_format))
    )
    df_cdr_details["call_time"] = df_cdr["time_start"].apply(
        lambda x: dt.time(dt.strptime(x, date_format))
    )
    df_cdr_details["call_week"] = (
        pd.to_datetime(df_cdr["time_start"], format=date_format).dt.isocalendar().week
    )
    df_cdr_details["day_of_week"] = df_cdr["time_start"].apply(
        lambda x: format_date(dt.strptime(x, date_format), "EEEE", locale=lang)
    )

    df_cdr_details = df_cdr_details.astype(
        {"handling_time_seconds": int, "waiting_time_seconds": int}
    )
    df_cdr_details["filename"] = filename

    df_cdr["time_start"] = df_cdr["time_start"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format))
    )
    #df_cdr["time_answered"] = np.where(
    #    df_cdr["time_answered"].isnull, None, df_cdr["time_answered"]
    #)
    df_cdr["time_answered"] = df_cdr["time_answered"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format)) if pd.notnull(x) else None
    )
    df_cdr["time_end"] = df_cdr["time_end"].apply(
        lambda x: to_local_datetime(dt.strptime(x, date_format))
    )
    df_cdr["from_dispname"] = df_cdr["from_dispname"].apply(str)
    df_cdr["to_dispname"] = df_cdr["to_dispname"].apply(str)
    df_cdr["final_dispname"] = df_cdr["final_dispname"].apply(str)
    df_cdr["final_number"] = df_cdr["final_number"].apply(str)

    cdr = df_cdr.to_json(orient="records", lines=True)
    cdr_details = df_cdr_details.to_json(orient="records", lines=True)

    logger.info(cdr)
    logger.info(cdr_details)

    return cdr, cdr_details

def push_cdr_api(cdr, cdr_details):

    """Fonction permettant de poster le CDR et son détail vers l'API
    Cette fonction teste si l'enregistrement existe avant de le poster

    Args:
        cdr (String): Json contenant le CDR 
        cdr_details (String) : Json contenant le détail du CDR

    Returns:
        _String_: Renvoi 2 String :
            - 1 le statut d'intégration CDR
            - 1 le statut d'intégration de CDR détail
    """
    base_url = CONFIG["api"]["base_url"]
    webapi_url_cdr = base_url + CONFIG["api"]["endpoints"]["cdr"]
    webapi_url_cdr_details = base_url + CONFIG["api"]["endpoints"]["cdr_details"]
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    cdrdict = json.loads(cdr)
    cdr_historyid = cdrdict['historyid']
    cdrddict = json.loads(cdr_details)
    cdrd_historyid = cdrddict['cdr_historyid']
    urlcdr = quote(f"{webapi_url_cdr}/historyid/{cdr_historyid}")
    getcdr = requests.get(f"{webapi_url_cdr}/historyid/{cdr_historyid}")
    urlcdrdetails = quote(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}")
    getcdrdetails = requests.get(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}")
    logger.info(f"Status get cdr: {getcdr.status_code}")
    logger.info(f"Status get cdrdetail {getcdrdetails.status_code}")

    if getcdr.status_code == 404:
        r_cdr = requests.post(webapi_url_cdr,data=cdr, headers=headers)
        logger.info(f"Statut get cdr {r_cdr.status_code}")
        logger.info(f"Texte statut get cdr {r_cdr.content}")
        mcdr=r_cdr.status_code
    else:
        logger.info("cdr existant")
        mcdr ="cdr existant"
    if getcdrdetails.status_code == 404 and r_cdr.status_code == 200 :
        r_cdrdetails = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers)
        logger.info(r_cdrdetails.status_code)
        logger.info(r_cdrdetails.content)
        mcdrdetails = r_cdrdetails.status_code
    else :
        logger.info("cdr detail existant")
        mcdrdetails="cdr detail existant"

    return mcdr, mcdrdetails


def validate_cdr(cdr, cdr_details):
    """
    Validates CDR and CDR details data by sending them to dedicated validation endpoints.

    This implementation replaces the previous in-memory validation approach for several reasons:
    1. Centralizes validation logic at the API level to ensure consistent validation rules
    2. Allows validation rules to be updated without requiring client code changes
    3. Leverages the same validation used during direct API submissions
    4. Reduces code duplication between client and server components

    If the API validation endpoints are unavailable, falls back to basic validation checks.

    Args:
        cdr (str): JSON string containing CDR data
        cdr_details (str): JSON string containing CDR details data

    Returns:
        bool: True if validation passes, False otherwise
    """
    webapi_url_cdr = os.environ.get('API_URL') + '/v1/cdr/validate'
    webapi_url_cdr_details = os.environ.get('API_URL') + '/v1/cdrdetails/validate'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    try:
        # Primary validation method: API endpoints
        cdr_validation = requests.post(webapi_url_cdr, data=cdr, headers=headers)
        cdr_validation.raise_for_status()

        cdr_details_validation = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers)
        cdr_details_validation.raise_for_status()

        return True
    except requests.exceptions.ConnectionError as e:
        # Connection to API failed, log warning and fall back to basic validation
        logger.exception(f"API validation unavailable, falling back to basic validation: {str(e)}")
        return perform_basic_validation(cdr, cdr_details)
    except requests.exceptions.HTTPError as e:
        # API returned an error response - check if it's a server error (5xx)
        if e.response.status_code >= 500:
            logger.error(f"API server error during validation (code {e.response.status_code}): {str(e)}")
            logger.warning("Falling back to basic validation due to API server error")
            return perform_basic_validation(cdr, cdr_details)
        else:
            # Client error (4xx) - likely a validation failure, log details from response if available
            try:
                error_details = e.response.json()
                logger.error(f"Validation error (code {e.response.status_code}): {error_details}")
            except ValueError:
                logger.error(f"Validation error (code {e.response.status_code}): {str(e)}")
            return False
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"Unexpected error during validation: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.warning("Falling back to basic validation due to unexpected error")
        return perform_basic_validation(cdr, cdr_details)


def perform_basic_validation(cdr, cdr_details):
    """
    Performs basic validation of CDR and CDR details when API validation is unavailable.

    This is a simplified version of the original validation logic that checks for
    required fields and basic data integrity.

    Args:
        cdr (str): JSON string containing CDR data
        cdr_details (str): JSON string containing CDR details data

    Returns:
        bool: True if basic validation passes, False otherwise
    """
    try:
        # Parse JSON strings
        cdr_data = json.loads(cdr)
        cdr_details_data = json.loads(cdr_details)

        # Check required fields in CDR
        required_cdr_fields = ["historyid", "callid", "time_start", "time_end"]
        for field in required_cdr_fields:
            if field not in cdr_data or cdr_data[field] is None:
                logger.error(f"Missing required CDR field: {field}")
                return False

        # Check required fields in CDR details
        required_details_fields = ["cdr_historyid"]
        for field in required_details_fields:
            if field not in cdr_details_data or cdr_details_data[field] is None:
                logger.error(f"Missing required CDR details field: {field}")
                return False

        # Verify historyid matches between CDR and CDR details
        if cdr_data["historyid"] != cdr_details_data["cdr_historyid"]:
            logger.error("Mismatch between CDR historyid and CDR details cdr_historyid")
            return False

        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Basic validation error: {str(e)}")
        return False
def push_cdr_api2(cdr, cdr_details):

    """Fonction permettant de poster le CDR et son détail vers l'API
    Cette fonction teste si l'enregistrement existe avant de le poster

    Args:
        cdr (String): Json contenant le CDR 
        cdr_details (String) : Json contenant le détail du CDR

    Returns:
        _String_: Renvoi 2 Srting :
            - 1 le statut d'intégration CDR
            - 1 le statut d'intégration de CDR détail
    """

    webapi_url_cdr = os.environ.get('API_URL') + '/v1/cdr'
    webapi_url_cdr_details = os.environ.get('API_URL') + '/v1/cdrdetails'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    cdrdict = json.loads(cdr)
    cdr_historyid = cdrdict['historyid']
    cdrddict = json.loads(cdr_details)
    cdrd_historyid = cdrddict['cdr_historyid']


    try:
        getcdr = requests.get(f"{webapi_url_cdr}/historyid/{cdr_historyid}")
        getcdr.raise_for_status()
    except HTTPError as http_err:
        if http_err.response.status_code == 422:
            logger.error(f"Erreur 422 (Unprocessable Entity) lors de la récupération du CDR: {http_err}")
            mcdr = http_err.response.status_code
        else:
            logger.error(f"Erreur HTTP lors de la récupération du CDR: {http_err}")
            mcdr = http_err.response.status_code
    else:
        logger.info(getcdr.status_code)
        if getcdr.status_code == 404:
            try:
                r_cdr = requests.post(webapi_url_cdr, data=cdr, headers=headers)
                r_cdr.raise_for_status()
            except HTTPError as http_err:
                if http_err.response.status_code == 422:
                    logger.error(f"Erreur 422 (Unprocessable Entity) lors de l'envoi du CDR: {http_err}")
                    mcdr = "Erreur 422"
                else:
                    logger.error(f"Erreur HTTP lors de l'envoi du CDR: {http_err}")
                    mcdr = "Erreur HTTP"
            else:
                logger.info(r_cdr.status_code)
                logger.info(r_cdr.content)
                mcdr = r_cdr.status_code
        else:
            logger.info("cdr existant")
            mcdr = "cdr existant"

    try:
        getcdrdetails = requests.get(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}")
        getcdrdetails.raise_for_status()
    except HTTPError as http_err:
        if http_err.response.status_code == 422:
            logger.error(f"Erreur 422 (Unprocessable Entity) lors de la récupération du CDR: {http_err}")
            mcdrdetails = http_err.response.status_code
        else:
            logger.error(f"Erreur HTTP lors de la récupération du CDR: {http_err}")
            mcdrdetails = http_err.response.status_code
    else:
        logger.info(getcdrdetails.status_code)
        if getcdrdetails.status_code == 404:
            try:
                r_cdrdetails = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers)
                r_cdrdetails.raise_for_status()
            except HTTPError as http_err:
                if http_err.response.status_code == 422:
                    logger.error(f"Erreur 422 (Unprocessable Entity) lors de l'envoi du CDR: {http_err}")
                    mcdrdetails = "Erreur 422"
                else:
                    logger.error(f"Erreur HTTP lors de l'envoi du CDR: {http_err}")
                    mcdrdetails = "Erreur HTTP"
            else:
                logger.info(r_cdr.status_code)
                logger.info(r_cdr.content)
                mcdrdetails = r_cdrdetails.status_code
        else:
            logger.info("cdr existant")
            mcdrdetails = "cdr existant"


    return mcdr, mcdrdetails