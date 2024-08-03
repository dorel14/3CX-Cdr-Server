import streamlit as st
import streamlit_antd_components as sac
import sys
import os
from modulus.extensions_view import Extensions
from modulus.queues_view import Queues

sys.path.append(os.path.abspath("."))
from modules.version import __version__
host= os.environ.get('NGINX_SERVER_NAME')


st.set_page_config(
    page_title="3CX CDR Server app",
    layout='wide',
    page_icon='🤷',
    menu_items={
        'about': f'''App resume : 3CX CDR Server app is a simple app to store Call Data Records (CDR) from 3CX **  
        Version {__version__}*'''
    }
)

def Home():
    st.header('Welcome to 3CX CDR Server app')

    st.markdown('''3CX CDR Server app is a simple app to store Call Data Records (CDR) from 3CX. 
                You can also make some reporting with Grafana .''')

    st.markdown('Here are the differents Urls you can use : ')
    st.markdown(f'- Api docs : http://{host}/api/docs')
    st.markdown(f'- Pg Admin : http://{host}/pgadmin')
    st.markdown(f'- Grafana : http://{host}/grafana')
    
def main():
    with st.sidebar:
        menu_item = sac.menu(
            index=0,  # refers to the Home
            open_all=False,
            color='indigo',
            items=[
                sac.MenuItem('Home', icon='house-fill'),

                sac.MenuItem(
                    '3cx Parameters',
                    icon='bi bi-headset',
                    children=[
                        sac.MenuItem('Extensions', icon='people'),
                        sac.MenuItem('Queues', icon='bi bi-hourglass-split'),
                    ]
                ),

                #sac.MenuItem('Account', icon='credit-card-2-front-fill'),

            ],        
        )


    menu_actions = {
        'Home': Home,
        'Extensions': Extensions,
        'Queues': Queues,

    }

    if menu_item in menu_actions:
        menu_actions[menu_item]()


if __name__ == '__main__':
    main()

