# -*- coding: UTF-8 -*-

import streamlit as st
import requests

import pandas as pd
import os
import sys


def Queues():
    sys.path.append(os.path.abspath("."))
    from myhelpers.queues_import import post_queues

    api_base_url = os.environ.get('API_URL')

    Tab1, Tab2, Tab3 = st.tabs(
        ["Queues View", "Queues Import", "Queues Add or Edit"])
    with Tab1:
        st.header("Queues View")
        queues = requests.get(f"{api_base_url}/api/v1/queues").json()
        if not queues:
            headers = ["queue", "queuename"]
            df = pd.DataFrame(columns=headers)
            st.dataframe(df,
                        use_container_width=True
                           )
        else:    
            st.dataframe(queues,
                           use_container_width=True)
    with Tab2:
        st.header("Queues Import")
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
            st.button(label='Import', on_click=post_queues(df))
    with Tab3:
        st.header("Queues Add or Edit")
        st.write("Ajouter ou modifier une queue")
        queues = requests.get(f"{api_base_url}/api/v1/queues").json()
        if not queues:
            headers = ["queue", "queuename"]
            df = pd.DataFrame(columns=headers)
            edited_df = st.data_editor(df,
                                       use_container_width=True,
                                       num_rows="dynamic")
            csv=df.to_csv(index=False)
            left_column, right_column = st.columns(2)
            left_column.download_button(
                label="Download template CSV",
                data=csv,
                file_name='queues.csv',
                mime='text/csv'
                )
            right_column.button(label="Save",
                                on_click=post_queues(edited_df))
        else:
            edited_df = st.data_editor(queues,
                                       use_container_width=True,
                                       num_rows="dynamic")
            left_column,right_column = st.columns(2)
            left_column.button(label="Save",
                               on_click=post_queues(edited_df))

    