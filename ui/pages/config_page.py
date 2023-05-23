import streamlit as st
import requests
import json
from app import api_base_url

sections = requests.get(f"{api_base_url}/config/sections")

st.write(sections.)

db_type = st.selectbox(label='Type de base de donnée',
             options=('sqlite', 'PostGresql'))

if db_type == 'PostGresql':
    server_adress = st.text_input(label='Adresse du serveur')
    server_port = st.text_input(label='Port',
                  value='5432')
    postgres_user = st.text_input(label='Utilisateur BD')
    postgres_password = st.text_input(label='Mot de passse BD',
                                      type='password')
    settings=dict(server=server_adress,
            port=server_port,
            user=postgres_user,
            password=postgres_password
            )
else:
    db_path = st.text_input(label='Répertoire de la base de donnée',
                            value='./db_folder/cdr3cxdb')
    settings=dict(section=db_path)


st.button(label='Valider',
          on_click=requests.post(url=api_base_url,
                                 data=json.dumps(settings))
        )
                  

