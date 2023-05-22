import streamlit as st
from helpers.configsave import saveDbInfos

db_type = st.selectbox(label='Type de base de donnée',
             options=('sqlite', 'PostGresql'))

if db_type == 'PostGresql':
    server_adress = st.text_input(label='Adresse du serveur')
    server_port = st.text_input(label='Port',
                  value='5432')
    postgres_user = st.text_input(label='Utilisateur BD')
    postgres_password = st.text_input(label='Mot de passse BD',
                                      type='password')
    kwargs=dict(server=server_adress,
            port=server_port,
            user=postgres_user,
            password=postgres_password
            )
else:
    db_path = st.text_input(label='Répertoire de la base de donnée',
                            value='./db_folder/cdr3cxdb')
    kwargs=dict(path=db_path
                )


st.button(label='Valider',
          on_click=saveDbInfos(db_type))
                  

