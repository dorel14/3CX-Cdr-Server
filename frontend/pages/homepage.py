from .generals.message import message

from nicegui import ui
import os

host= os.environ.get('WEB_SERVER_NAME')

def content() -> None:
    message('Welcome to 3CX CDR Server app').classes('font-bold text-4xl text-grey-8')

    ui.markdown('''3CX CDR Server app is a simple app to store Call Data Records (CDR) from 3CX. 
                You can also make some reporting with Grafana .''')
    
    ui.markdown('Here are the differents Urls you can use : ')
    with ui.column():
        ui.button('- Api docs', on_click=lambda: ui.navigate.to(f'http://{host}/webapi/docs', new_tab=True)).classes('flat')
        ui.button('- Pg Admin', on_click=lambda: ui.navigate.to(f'http://{host}/pgadmin', new_tab=True)).classes('flat')
        ui.button('- Grafana', on_click=lambda: ui.navigate.to(f'http://{host}/grafana', new_tab=True)).classes('flat')
        ui.button('- Traefik', on_click=lambda: ui.navigate.to(f'http://{host}/dashboard/', new_tab=True)).classes('flat')
        
