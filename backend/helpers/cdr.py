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

    try:
        cdrdict = json.loads(cdr)
        cdr_historyid = cdrdict['historyid']
        cdrddict = json.loads(cdr_details)
        cdrd_historyid = cdrddict['cdr_historyid']
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON: {str(e)}")
        return "Erreur JSON", "Erreur JSON"
    except KeyError as e:
        logger.error(f"Clé manquante dans les données JSON: {str(e)}")
        return "Données incomplètes", "Données incomplètes"

    mcdr = "Erreur API"
    mcdrdetails = "Erreur API"

    # Vérification de l'existence du CDR
    try:
        urlcdr = quote(f"{webapi_url_cdr}/historyid/{cdr_historyid}")
        getcdr = requests.get(f"{webapi_url_cdr}/historyid/{cdr_historyid}", timeout=10)
        logger.info(f"Status get cdr: {getcdr.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la vérification du CDR: {str(e)}")
        return "Erreur connexion API", "Erreur connexion API"

    # Vérification de l'existence du détail CDR
    try:
        urlcdrdetails = quote(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}")
        getcdrdetails = requests.get(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}", timeout=10)
        logger.info(f"Status get cdrdetail {getcdrdetails.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la vérification du détail CDR: {str(e)}")
        return mcdr, "Erreur connexion API"

    # Traitement du CDR
    if getcdr.status_code == 404:
        try:
            r_cdr = requests.post(webapi_url_cdr, data=cdr, headers=headers, timeout=10)
            r_cdr.raise_for_status()  # Raise an exception for 4XX/5XX responses
            logger.info(f"Statut post cdr {r_cdr.status_code}")
            logger.info(f"Texte statut post cdr {r_cdr.content}")
            mcdr = r_cdr.status_code
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'envoi du CDR: {str(e)}")
            mcdr = f"Erreur HTTP: {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'envoi du CDR: {str(e)}")
            mcdr = "Erreur envoi CDR"
    else:
        logger.info("cdr existant")
        mcdr = "cdr existant"

    # Traitement du détail CDR - seulement si le CDR a été posté avec succès
    if getcdrdetails.status_code == 404 and (mcdr == 200 or mcdr == 201):
        try:
            r_cdrdetails = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers, timeout=10)
            r_cdrdetails.raise_for_status()
            logger.info(f"Statut post cdr details: {r_cdrdetails.status_code}")
            logger.info(f"Texte statut post cdr details: {r_cdrdetails.content}")
            mcdrdetails = r_cdrdetails.status_code
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'envoi du détail CDR: {str(e)}")
            mcdrdetails = f"Erreur HTTP: {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'envoi du détail CDR: {str(e)}")
            mcdrdetails = "Erreur envoi détail CDR"
    else:
        logger.info("cdr detail existant ou CDR non posté")
        mcdrdetails = "cdr detail existant"

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
    # First, validate that inputs are valid JSON before sending to API
    try:
        # Try parsing the JSON to catch format errors early
        json.loads(cdr)
        json.loads(cdr_details)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format detected before API validation: {str(e)}")
        logger.debug(f"Problematic JSON sample (CDR): {cdr[:100]}...")
        logger.debug(f"Problematic JSON sample (CDR details): {cdr_details[:100]}...")
        return False

    webapi_url_cdr = CONFIG["api"]["base_url"] + '/v1/cdr/validate'
    webapi_url_cdr_details = CONFIG["api"]["base_url"] + '/v1/cdr/validate/details'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    try:
        # Primary validation method: API endpoints
        logger.info("Attempting API validation for CDR data")
        cdr_validation = requests.post(webapi_url_cdr, data=cdr, headers=headers)

        if not cdr_validation.ok:
            # Enhanced logging for API validation failures
            logger.error(f"CDR validation failed with status code: {cdr_validation.status_code}")
            try:
                error_details = cdr_validation.json()
                logger.error(f"CDR validation error details: {json.dumps(error_details, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"CDR validation error response (non-JSON): {cdr_validation.text[:500]}")

        cdr_validation.raise_for_status()

        logger.info("Attempting API validation for CDR details data")
        cdr_details_validation = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers)

        if not cdr_details_validation.ok:
            # Enhanced logging for API validation failures
            logger.error(f"CDR details validation failed with status code: {cdr_details_validation.status_code}")
            try:
                error_details = cdr_details_validation.json()
                logger.error(f"CDR details validation error details: {json.dumps(error_details, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"CDR details validation error response (non-JSON): {cdr_details_validation.text[:500]}")

        cdr_details_validation.raise_for_status()

        logger.info("API validation successful for both CDR and CDR details")
        return True
    except json.JSONDecodeError as e:
        # This could happen if the API response contains invalid JSON
        logger.error(f"JSON decode error during API validation: {str(e)}")
        logger.warning("Falling back to basic validation due to API response JSON error")
        return perform_basic_validation(cdr, cdr_details)
    except requests.exceptions.ConnectionError as e:
        # Connection to API failed, log warning and fall back to basic validation
        logger.warning(f"API validation unavailable (connection error): {str(e)}")
        logger.info("Falling back to basic validation")
        return perform_basic_validation(cdr, cdr_details)
    except requests.exceptions.Timeout as e:
        # API request timed out
        logger.warning(f"API validation timed out: {str(e)}")
        logger.info("Falling back to basic validation due to timeout")
        return perform_basic_validation(cdr, cdr_details)
    except requests.exceptions.HTTPError as e:
        # API returned an error response - check if it's a server error (5xx)
        if e.response.status_code >= 500:
            logger.error(f"API server error during validation (code {e.response.status_code}): {str(e)}")
            logger.info("Falling back to basic validation due to API server error")
            return perform_basic_validation(cdr, cdr_details)
        else:
            # Client error (4xx) - likely a validation failure, log details from response if available
            try:
                error_details = e.response.json()
                logger.error(f"Validation error (code {e.response.status_code}): {json.dumps(error_details, indent=2)}")
                # Log specific validation errors if available in a structured format
                if isinstance(error_details, dict) and 'detail' in error_details:
                    if isinstance(error_details['detail'], list):
                        for error in error_details['detail']:
                            logger.error(f"Field '{error.get('loc', ['unknown'])}': {error.get('msg', 'Unknown error')}")
                    else:
                        logger.error(f"Validation detail: {error_details['detail']}")
            except json.JSONDecodeError:
                # Handle case where error response is not valid JSON
                logger.error(f"Validation error (code {e.response.status_code}): {e.response.text}")
            except Exception as parse_err:
                logger.error(f"Error parsing validation response: {str(parse_err)}")
                logger.error(f"Raw response: {e.response.text[:200]}...")
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

    This function orchestrates multiple validation checks by calling specialized
    validation functions for different aspects of the data.

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

        logger.info("Performing basic validation as fallback")

        # Run validation checks in sequence
        validation_checks = [
            validate_required_fields(cdr_data, cdr_details_data),
            validate_data_types(cdr_data),
            validate_id_consistency(cdr_data, cdr_details_data),
            validate_time_sequence(cdr_data),
            validate_numeric_values(cdr_details_data)
        ]

        # If any validation check returns False, validation fails
        if not all(validation_checks):
            return False

        logger.info("Basic validation passed successfully")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {str(e)}")
        logger.debug(f"Problematic JSON (CDR): {cdr[:100]}...")
        logger.debug(f"Problematic JSON (CDR details): {cdr_details[:100]}...")
        return False
    except Exception as e:
        logger.error(f"Basic validation error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


def validate_required_fields(cdr_data, cdr_details_data):
    """Validates that all required fields are present and non-null."""
    try:
        # Check required fields in CDR
        required_cdr_fields = ["historyid", "callid", "time_start", "time_end", "duration"]
        for field in required_cdr_fields:
            if field not in cdr_data:
                logger.error(f"Missing required CDR field: {field}")
                return False
            if cdr_data[field] is None:
                logger.error(f"Required CDR field '{field}' has null value")
                return False

        # Check required fields in CDR details
        required_details_fields = ["cdr_historyid", "call_date", "call_time", "handling_time_seconds", "waiting_time_seconds"]
        for field in required_details_fields:
            if field not in cdr_details_data:
                logger.error(f"Missing required CDR details field: {field}")
                return False
            if cdr_details_data[field] is None and field != "call_time":  # call_time can be null in some cases
                logger.error(f"Required CDR details field '{field}' has null value")
                return False

        return True
    except KeyError as e:
        logger.error(f"Key error while validating required fields: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error validating required fields: {str(e)}")
        return False


def validate_data_types(cdr_data):
    """Validates that data fields have the correct types."""
    try:
        # Validate historyid is numeric
        if not str(cdr_data["historyid"]).isdigit():
            logger.error(f"Invalid historyid format: {cdr_data['historyid']} - must be numeric")
            return False

        # Validate time fields are valid datetime strings
        for time_field in ["time_start", "time_end"]:
            if pd.isna(cdr_data[time_field]) or not isinstance(cdr_data[time_field], str):
                logger.error(f"Invalid {time_field} format: must be a valid datetime string")
                return False

        # Validate time_answered if present
        if "time_answered" in cdr_data and cdr_data["time_answered"] is not None:
            if not isinstance(cdr_data["time_answered"], str):
                logger.error("Invalid time_answered format: must be a valid datetime string")
                return False

        # Validate duration is numeric
        if not str(cdr_data["duration"]).replace(".", "", 1).isdigit():
            logger.error(f"Invalid duration format: {cdr_data['duration']} - must be numeric")
            return False

        return True
    except Exception as e:
        logger.error(f"Data type validation error: {str(e)}")
        return False


def validate_id_consistency(cdr_data, cdr_details_data):
    """Validates that IDs are consistent between CDR and CDR details."""
    try:
        # Verify historyid matches between CDR and CDR details
        if str(cdr_data["historyid"]) != str(cdr_details_data["cdr_historyid"]):
            logger.error(f"Mismatch between CDR historyid ({cdr_data['historyid']}) and CDR details cdr_historyid ({cdr_details_data['cdr_historyid']})")
            return False

        return True
    except KeyError as e:
        logger.error(f"Key error while validating ID consistency: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error validating ID consistency: {str(e)}")
        return False


def validate_time_sequence(cdr_data):
    """Validates that time fields follow a logical sequence."""
    try:
        time_start = pd.to_datetime(cdr_data["time_start"])
        time_end = pd.to_datetime(cdr_data["time_end"])

        if time_start > time_end:
            logger.error(f"Invalid time sequence: time_start ({time_start}) is after time_end ({time_end})")
            return False

        # If time_answered exists, validate it's between start and end
        if "time_answered" in cdr_data and cdr_data["time_answered"] is not None:
            time_answered = pd.to_datetime(cdr_data["time_answered"])
            if time_answered < time_start or time_answered > time_end:
                logger.error(f"Invalid time_answered: {time_answered} is not between time_start ({time_start}) and time_end ({time_end})")
                return False

        return True
    except Exception as e:
        logger.error(f"Time sequence validation error: {str(e)}")
        return False


def validate_numeric_values(cdr_details_data):
    """Validates that numeric fields have valid values."""
    try:
        handling_time = float(cdr_details_data["handling_time_seconds"])
        waiting_time = float(cdr_details_data["waiting_time_seconds"])

        if handling_time < 0:
            logger.error(f"Invalid handling_time_seconds: {handling_time} (must be non-negative)")
            return False

        if waiting_time < 0:
            logger.error(f"Invalid waiting_time_seconds: {waiting_time} (must be non-negative)")
            return False

        return True
    except ValueError:
        logger.error("Invalid numeric format for handling_time_seconds or waiting_time_seconds")
        return False
    except KeyError as e:
        logger.error(f"Missing numeric field: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Numeric field validation error: {str(e)}")
        return False

def push_cdr_api2(cdr, cdr_details):
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
    if 'API_URL' not in CONFIG:
        logger.error("API_URL not configured in CONFIG")
        raise ValueError("API_URL not configured") # Or a custom exception
    webapi_url_cdr = CONFIG['API_URL'] + '/v1/cdr'
    webapi_url_cdr_details = CONFIG['API_URL'] + '/v1/cdr_details'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    try:
        cdrdict = json.loads(cdr)
        cdr_historyid = cdrdict['historyid']
        cdrddict = json.loads(cdr_details)
        cdrd_historyid = cdrddict['cdr_historyid']
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON: {str(e)}")
        return f"Erreur JSON: {str(e)}", "Erreur JSON"
    except KeyError as e:
        logger.error(f"Clé manquante dans les données JSON: {str(e)}")
        return f"Données incomplètes: {str(e)}", "Données incomplètes"

    mcdr = "Erreur API"
    mcdrdetails = "Erreur API"

    # Vérification de l'existence du CDR
    try:
        getcdr = requests.get(f"{webapi_url_cdr}/historyid/{cdr_historyid}", timeout=10)
        logger.info(f"Status get cdr: {getcdr.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la vérification du CDR: {str(e)}")
        return "Erreur connexion API", "Erreur connexion API"

    # Vérification de l'existence du détail CDR
    try:
        getcdrdetails = requests.get(f"{webapi_url_cdr_details}/historyid/{cdrd_historyid}", timeout=10)
        logger.info(f"Status get cdrdetail: {getcdrdetails.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la vérification du détail CDR: {str(e)}")
        return mcdr, "Erreur connexion API"

    # Traitement du CDR
    if getcdr.status_code == 404:
        try:
            r_cdr = requests.post(webapi_url_cdr, data=cdr, headers=headers, timeout=10)
            r_cdr.raise_for_status()
            logger.info(f"Statut post cdr: {r_cdr.status_code}")
            logger.info(f"Texte statut post cdr: {r_cdr.content}")
            mcdr = r_cdr.status_code
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'envoi du CDR: {str(e)}")
            mcdr = f"Erreur HTTP: {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'envoi du CDR: {str(e)}")
            mcdr = "Erreur envoi CDR"
    else:
        logger.info("CDR existant")
        mcdr = "CDR existant"

    # Traitement du détail CDR - seulement si le CDR a été posté avec succès
    if getcdrdetails.status_code == 404 and (mcdr == 200 or mcdr == 201):
        try:
            r_cdrdetails = requests.post(webapi_url_cdr_details, data=cdr_details, headers=headers, timeout=10)
            r_cdrdetails.raise_for_status()
            logger.info(f"Statut post cdr details: {r_cdrdetails.status_code}")
            logger.info(f"Texte statut post cdr details: {r_cdrdetails.content}")
            mcdrdetails = r_cdrdetails.status_code
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'envoi du détail CDR: {str(e)}")
            mcdrdetails = f"Erreur HTTP: {e.response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'envoi du détail CDR: {str(e)}")
            mcdrdetails = "Erreur envoi détail CDR"
    else:
        logger.info("CDR detail existant ou CDR non posté")
        mcdrdetails = "CDR detail existant"

    return mcdr, mcdrdetails