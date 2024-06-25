import streamlit as st
import requests
import pandas as pd
import os


from app import api_base_url


st.write("Uploader la liste des extensions à uploader au format csv")
uploaded_file = st.file_uploader("Uploader le fichier", type="csv",)


if uploaded_file:
    if not os.path.exists("/data/files"):
        os.makedirs("/data/files/", exist_ok=True)
    # Enregistrer le fichier dans le dossier "uploads"
    with open("/data/files/extensions.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.dataframe(pd.read_csv(uploaded_file))



