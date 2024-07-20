# -*- coding: UTF-8 -*-

import streamlit as st
import requests

import pandas as pd
import os
import sys


def Queues():
    sys.path.append(os.path.abspath("."))

    api_base_url = os.environ.get('API_URL')

    Tab1, Tab2, tab3 = st.tabs(
        ["Queues View", "Queues Import", "Queues ?"])
    with Tab1:
        st.header("Queues View")
        queues = requests.get(f"{api_base_url}/api/v1/queues").json()
        if not queues:
            headers = ["queue", "queuename"]
            df = pd.DataFrame(columns=headers)
            st.dataframe(df)
            csv=df.to_csv(index=False)
            st.download_button(
                label="Download template CSV",
                data=csv,
                file_name='queues.csv',
                mime='text/csv',
            )
        else:    
            st.dataframe(queues)
    with Tab2:
        st.header("Queues Import")
        from myhelpers.queues_import import post_queues
        st.write("Uploader la liste des queues à uploader au format csv")
        uploaded_file = st.file_uploader("Uploader le fichier", type="csv",)
        if uploaded_file:
            if not os.path.exists("/data/files"):
                os.makedirs("/data/files/", exist_ok=True)
            # Enregistrer le fichier dans le dossier "uploads"
            with open("/data/files/queues.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            df=pd.read_csv(uploaded_file)
            st.dataframe(df)
            st.button(label='Valider', on_click=post_queues(df))
    