import streamlit as st
import streamlit_antd_components as sac
import sys
import os
from dotenv import load_dotenv
from modulus.Extensions import Extensions

sys.path.append(os.path.abspath("."))
from modules.version import __version__
load_dotenv()


st.set_page_config(
    page_title="3CX CDR Server app",
    layout='centered',
    page_icon='🤷',
    menu_items={
        'about': f'''App resume \: Cette application permet de stocker les Call Data Records issus de 3CX **  
        Version {__version__}*'''
    }
)

def Home():
    st.header('Welcome to 3CX CDR Server app')

    st.markdown('''3CX CDR Server app is a simple app to store Call Data Records (CDR) from 3CX.''')

def main():
    with st.sidebar:
        menu_item = sac.menu(
            index=0,  # refers to the Home
            open_all=False,
            items=[
                sac.MenuItem('Home', icon='house-fill'),

                sac.MenuItem(
                    '3cx Parameters',
                    icon='box-fill',
                    children=[
                        sac.MenuItem('Extensions', icon='people'),

                        #sac.MenuItem(
                        #    'Google',
                        #    icon='google',
                        #    children=[
                        #        sac.MenuItem('Android', icon='android2'),
                        #        sac.MenuItem('Finance', icon='bank'),
                        #    ],
                        #),

                        #sac.MenuItem('Samsung', icon='phone-flip'),
                    ]
                ),

                #sac.MenuItem('Account', icon='credit-card-2-front-fill'),

            ],        
        )


    menu_actions = {
        'Home': Home,
        'Extensions': Extensions,

    }

    if menu_item in menu_actions:
        menu_actions[menu_item]()


if __name__ == '__main__':
    main()

