from message import message

from nicegui import ui
import os

host= os.environ.get('WEB_SERVER_NAME')

def content() -> None:
    message('Welcome to 3CX CDR Server app').classes('font-bold text-4xl text-grey-8')

    ui.markdown('''3CX CDR Server app is a simple app to store Call Data Records (CDR) from 3CX. 
                You can also make some reporting with Grafana .''')
    
    ui.markdown('Here are the differents Urls you can use : ')
    with ui.column():
        ui.link('- Api docs', f'http://{host}/api/docs').classes('text-black-500')
        ui.link('- Pg Admin', f'http://{host}/pgadmin')
        ui.link('- Grafana', f'http://{host}/grafana')
        ui.link('- Traefik', f'http://{host}/dashboard')
