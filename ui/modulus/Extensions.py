# -*- coding: UTF-8 -*-

from operator import index
from re import A
import streamlit as st
import requests

import pandas as pd
import os
import sys



def Extensions():
    sys.path.append(os.path.abspath("."))
    from myhelpers.logging import logger

    api_base_url = os.environ.get('API_URL')
    
    Tab1, Tab2, tab3 = st.tabs(
        ["Extensions View", "Extensions Import", "Extensions ?"])

    with Tab1:
        st.header("Extensions View")
        extensions = requests.get(f"{api_base_url}/api/v1/extensions").json()
        st.dataframe(extensions)

    with Tab2:
        st.header("Extensions Import")
        from myhelpers.extensions_import import post_extensions
           


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



