# -*- coding: UTF-8 -*-


import streamlit as st
import requests

import pandas as pd
import os
import sys

sys.path.append(os.path.abspath("."))
from myhelpers.queues_import import post_queues


def data_editor_getchanged(original_df, result_df): 
    #result_df = ss.edited_df
    print("original_df: ", original_df)
    print("result_df: ", result_df)
    final_df = pd.concat([original_df, result_df]).drop_duplicates(keep=False).reset_index(drop=True)
    final_df = final_df.drop_duplicates(keep='last', subset=['id']).reset_index(drop=True)
    print("final_df: ", final_df)
    post_queues(final_df)

def Queues():
    """
    The `Queues()` function is the main entry point for the Queues view in the application. It sets up three tabs: "Queues View", "Queues Import", and "Queues Add or Edit". Each tab contains functionality related to managing queues in the system.

    The "Queues View" tab displays a table of existing queues fetched from the API. If no queues are available, an empty dataframe is displayed.

    The "Queues Import" tab allows the user to upload a CSV file containing queue data. The uploaded file is saved to the "/data/files/" directory, and the data is displayed in a dataframe. A button is provided to initiate the import process.

    The "Queues Add or Edit" tab provides a data editor interface for creating or modifying queue data. If no queues exist, a blank dataframe is displayed, and the user can add new queues. If queues exist, the existing data is displayed in the data editor, and the user can make changes. A button is provided to save the changes, but the functionality is not yet implemented.
    """


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
                                on_click=data_editor_getchanged,
                                args=(df,edited_df ))
        else:
            df = pd.DataFrame(queues)
            edited_df = st.data_editor(df,
                                       use_container_width=True,
                                       num_rows="dynamic"
                                       )
            st.button(label="Save",
                               on_click=data_editor_getchanged,
                               args=(df,edited_df ))

    