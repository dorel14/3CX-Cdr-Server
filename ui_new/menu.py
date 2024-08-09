from nicegui import ui

def menu() -> None:
    with ui.list().props('bordered separator'):        
        ui.item_label('Menu').props('header').classes('text-bold')
        ui.separator()
        with ui.item(on_click=lambda: ui.open('/')):
            with ui.item_section().props('avatar'):
                ui.icon('house')
            with ui.item_section():
                ui.label('Home')
        with ui.expansion(text='3cx parameters'):
            with ui.item(on_click=lambda: ui.open('/extensions')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-headphone-alt')
                with ui.item_section():
                    ui.label('Extensions')
            with ui.item(on_click=lambda: ui.open('/queues')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-more')
                with ui.item_section():
                    ui.label('Queues')
            




        #with ui.row():
        #    ui.link('A', '/a').classes(replace='text-blue-500')
        #    ui.link('B', '/b').classes(replace='text-blue-500')
        #    ui.link('C', '/c').classes(replace='text-blue-500')
        #with ui.menu() as menu:
        #    ui.menu_item('About', on_click=about)