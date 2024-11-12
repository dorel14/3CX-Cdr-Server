# -*- coding: UTF-8 -*-

import json
import requests
import os
import pandas as pd
from requests.exceptions import HTTPError
from myhelpers.logging import logger


api_base_url = os.environ.get('API_URL')

def post_extensions(extensions:str | pd.DataFrame):
    """Fonction permettant de poster les extensions au serveur
    Cette fonction teste si l'enregistrement existe avant de le poster
    """

    if len(extensions) > 0:
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        webapi_url_extensions = api_base_url + '/v1/extensions'

        if isinstance(extensions, str):
            list_of_jsons=[extensions]
        elif isinstance(extensions, pd.DataFrame):
            list_of_jsons = extensions.to_json(orient='records', lines=True).splitlines()
            
        for js in list_of_jsons:
                logger.info(js)            
                try:
                    j = json.loads(js)
                    testextension = requests.get(f"{webapi_url_extensions}/byextension/{j["extension"]}")
                    if not testextension.status_code == 200:
                        response = requests.post(webapi_url_extensions, headers=headers, data=js)
                        response.raise_for_status()
                        logger.info(js)
                    elif testextension.status_code == 200:
                        logger.info(f"L'extension {j['extension']} existe déjà")
                        extensionid = testextension.json()['id']
                        response = requests.patch(f"{webapi_url_extensions}/{extensionid}", headers=headers, data=js)
                except HTTPError as http_err:
                    if http_err.response.status_code == 422:
                        logger.error(f"Erreur 422 (Unprocessable Entity) lors de la récupération de l'extension: {http_err}")
                    else:
                        logger.error(f"Erreur lors de l'intégration de l'extension: {http_err}")
                else:
                    logger.info(f"Extension {js} postée avec succès")
        return 'Successfully posted'