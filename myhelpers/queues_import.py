# -*- coding: UTF-8 -*-

import json
import requests
import os
import pandas as pd

from requests.exceptions import HTTPError
from myhelpers.logging import logger


api_base_url = os.environ.get('API_URL')

def post_queues(queues:str | pd.DataFrame):
    """Fonction permettant de poster les queues au serveur
    Cette fonction teste si l'enregistrement existe avant de le poster
    """
    if len(queues) > 0:
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        webapi_url_queues = api_base_url + '/v1/queues'
        list_of_jsons = queues.to_json(orient='records', lines=True).splitlines()
        for js in list_of_jsons:
                logger.info(js)
                try:
                    j = json.loads(js)
                    testqueue = requests.get(f"{webapi_url_queues}/byqueue/{j['queue']}")
                    if not testqueue.status_code == 200:
                        response = requests.post(webapi_url_queues, headers=headers, data=js)
                        response.raise_for_status()
                        logger.info(js)
                    elif testqueue.status_code == 200:
                        queueid = testqueue.json()['id']
                        logger.info(f"Queue {js} déjà présente")
                        response = requests.patch(f"{webapi_url_queues}/{queueid}", headers=headers, data=js)
                        logger.info(f"Queue {js} mise à jour avec succès")
                    else:
                        logger.info(f"Queue {js} postée avec succès")
                except HTTPError as http_err:
                    if http_err.response.status_code == 422:
                        logger.error(f"Erreur 422 (Unprocessable Entity) lors de la récupération de la queue: {http_err}")
                    else:
                        logger.error(f"Erreur lors de l'intégration de la queue: {http_err}")
                else:
                    logger.info(f"Queue {js} postée avec succès")

