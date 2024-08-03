# -*- coding: UTF-8 -*-

import streamlit as st
import requests
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath("."))
from myhelpers.extensions_import import post_extensions

def data_editor_getchanged(original_df, result_df): 
    #result_df = ss.edited_df
    #print("original_df: ", original_df)
    #print("result_df: ", result_df)
    final_df = pd.concat([original_df, result_df]).drop_duplicates(keep=False).reset_index(drop=True)
    final_df = final_df.drop_duplicates(keep='last', subset=['id']).reset_index(drop=True)
    print("final_df: ", final_df)
    post_extensions(final_df)

def Extensions():
    api_base_url = os.environ.get('API_URL')
    
    Tab1, Tab2, Tab3 = st.tabs(
        ["Extensions View", "Extensions Import", "Extensions Add, Modify"])

    with Tab1:
        st.header("Extensions View")
        extensions = requests.get(f"{api_base_url}/api/v1/extensions").json()
        if not extensions:
            headers = ["extension", "name", "mail"]
            df = pd.DataFrame(columns=headers)
            st.dataframe(df,
                         use_container_width=True)
            csv=df.to_csv(index=False)
            st.download_button(
                label="Download template CSV",
                data=csv,
                file_name='extensions.csv',
                mime='text/csv',
            )
        else:
            st.dataframe(extensions,
                         use_container_width=True)

    with Tab2:
        st.header("Extensions Import")
        st.write("Uploader la liste des extensions à uploader au format csv")
        uploaded_extensions_file = st.file_uploader("Uploader le fichier", type="csv",key="extensions_file")

        if uploaded_extensions_file:
            if not os.path.exists("/data/files"):
                os.makedirs("/data/files/", exist_ok=True)
            # Enregistrer le fichier dans le dossier "uploads"
            with open("/data/files/extensions.csv", "wb") as f:
                f.write(uploaded_extensions_file.getbuffer())
            df=pd.read_csv(uploaded_extensions_file)
            st.dataframe(df,
                         use_container_width=True)
            st.button(label='Import', on_click=post_extensions(df))
    with Tab3:
        st.header("Extensions Add, Modify")
        extensions = requests.get(f"{api_base_url}/api/v1/extensions").json()
        if not extensions:
            headers = ["extension", "name", "mail"]
            df = pd.DataFrame(columns=headers)
            st.dataframe(df,
                         use_container_width=True)
            csv=df.to_csv(index=False)
            st.download_button(
                label="Download template CSV",
                data=csv,
                file_name='extensions.csv',
                mime='text/csv',
            )
        else:
            df=pd.DataFrame(extensions)
            edited_df = st.data_editor(df,
                                       column_config={
                                           "id" : None,                                           
                                       },
                                       num_rows="dynamic",
                                       use_container_width=True
                                       )
            st.button(label="Save",
                      on_click=data_editor_getchanged,
                      args=(df,edited_df ))



