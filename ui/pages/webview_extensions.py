import streamlit as st
import requests
import pandas as pd

from app import api_base_url

extensions = requests.get(f"{api_base_url}/api/v1/extensions")
st.dataframe(pd.read_json(extensions.text))