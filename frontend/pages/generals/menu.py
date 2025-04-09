from nicegui import ui

def menu() -> None:
    with ui.list().props('bordered separator'):        
        ui.item_label('Menu').props('header').classes('text-bold')
        ui.separator()
        with ui.item(on_click=lambda: ui.navigate.to('/')):
            with ui.item_section().props('avatar'):
                ui.icon('house')
            with ui.item_section():
                ui.label('Home')
        with ui.item(on_click=lambda: ui.navigate.to('/events')):
            with ui.item_section().props('avatar'):
                    ui.icon('ti-calendar')
            with ui.item_section():
                    ui.label('Events')
        with ui.expansion(text='3cx parameters', group='Menu'):
            with ui.item(on_click=lambda: ui.navigate.to('/extensions')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-headphone-alt')
                with ui.item_section():
                    ui.label('Extensions')
            with ui.item(on_click=lambda: ui.navigate.to('/queues')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-more')
                with ui.item_section():
                    ui.label('Queues')
        with ui.expansion(text='System parameters', group='Menu'):
            with ui.item(on_click=lambda: ui.navigate.to('/users')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-user')
                with ui.item_section():
                    ui.label('Users')
            with ui.item(on_click=lambda: ui.navigate.to('/event_types')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-calendar')
                with ui.item_section():
                    ui.label('Event Types')
            with ui.item(on_click=lambda: ui.navigate.to('/parameters')):
                with ui.item_section().props('avatar'):
                    ui.icon('ti-settings')
                with ui.item_section():
                    ui.label('Parameters')






        #with ui.row():
        #    ui.link('A', '/a').classes(replace='text-blue-500')
        #    ui.link('B', '/b').classes(replace='text-blue-500')
        #    ui.link('C', '/c').classes(replace='text-blue-500')
        #with ui.menu() as menu:
        #    ui.menu_item('About', on_click=about)