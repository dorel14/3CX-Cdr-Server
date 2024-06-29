from operator import index
import streamlit as st
import requests
from requests.exceptions import HTTPError
import pandas as pd
import os
import sys
import json


sys.path.append(os.path.abspath("."))
from myhelpers.logging import logger

st.set_page_config(page_title="Extensions", 
                   page_icon=":rocket:")

from app import api_base_url


def post_extensions(extensions):
    """Fonction permettant de poster les extensions au serveur
    Cette fonction teste si l'enregistrement existe avant de le poster
    """
    if not extensions.empty:
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        webapi_url_extensions = api_base_url + '/api/v1/extensions'
        
        list_of_jsons = df.to_json(orient='records', lines=True).splitlines()
        for js in list_of_jsons:
                logger.info(js)            
                try:
                    j = json.loads(js)
                    testextension = requests.get(f"{webapi_url_extensions}/byextension/{j["extension"]}")
                    if not testextension.status_code == 200:
                        response = requests.post(webapi_url_extensions, headers=headers, data=js)
                        response.raise_for_status()
                        logger.info(js)
                except HTTPError as http_err:
                    if http_err.response.status_code == 422:
                        logger.error(f"Erreur 422 (Unprocessable Entity) lors de la récupération de l'extension: {http_err}")
                    else:
                        logger.error(f"Erreur lors de l'intégration de l'extension: {http_err}")
                else:
                    logger.info(f"Extension {js} postée avec succès")


                


st.write("Uploader la liste des extensions à uploader au format csv")
uploaded_file = st.file_uploader("Uploader le fichier", type="csv",)




if uploaded_file:
    if not os.path.exists("/data/files"):
        os.makedirs("/data/files/", exist_ok=True)
    # Enregistrer le fichier dans le dossier "uploads"
    with open("/data/files/extensions.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
df=pd.read_csv(uploaded_file)
st.dataframe(df)

st.button(label='Valider', on_click=post_extensions(df))



