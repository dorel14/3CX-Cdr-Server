from contextlib import contextmanager

from .menu import menu

from nicegui import ui
from nicegui_tabulator import use_theme

from ...modules.version import __version__




@contextmanager
def frame(navigation_title: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#06358a', secondary='#057341', accent='#111B1E', positive='#53B689')
    ui.add_head_html('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">')
    ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
    ui.add_head_html('<link href="https://cdn.jsdelivr.net/themify-icons/0.1.2/css/themify-icons.css" rel="stylesheet" />')
    use_theme('semanticui') #tabulator theme for all tables
    with ui.dialog() as about, ui.card().classes('items-center'):
        ui.label('Informations').classes('text-lg')
        ui.label(f'Version {__version__}')
        ui.label('Made with ❤️ by David Orel')
        ui.button('', icon='close', on_click=about.close).classes('px-3 py-2 text-xs ml-auto ')

    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.space()
        ui.label(navigation_title).classes('font-bold') 
        ui.space()
        ui.button(on_click=about.open, icon='info').props('flat color=white')
    
    with ui.footer() as footer:
        ui.label('Footer')

    with ui.left_drawer().classes('bg-blue-50') as left_drawer:        
        with ui.column():
            menu()
    with ui.column().classes('absolute-center items-center'):
        yield
    
    #with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        #ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    
