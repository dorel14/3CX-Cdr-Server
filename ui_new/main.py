# -*- coding: UTF-8 -*-


import pages.homepage as homepage
import theme
import pages.extensions_view as extensions_view
import pages.queues_view as queues_view
import pages.events_view as events_view

from nicegui import app, ui
import os


# Example 1: use a custom page decorator directly and putting the content creation into a separate function
@ui.page('/')
def index_page() -> None:
    with theme.frame('Homepage'):
        homepage.content()
        ui.page_title("3CX CDR Server app")


# Example 2: use a function to move the whole page creation into a separate file
#function_example.create()

# Example 3: use a class to move the whole page creation into a separate file
#class_example.ClassExample()

# Example 4: use APIRouter as described in https://nicegui.io/documentation/page#modularize_with_apirouter
#app.include_router(api_router_example.router)
app.include_router(extensions_view.router)
app.include_router(queues_view.router)
app.include_router(events_view.router)

language = os.environ.get('LOCALE_LANGUAGE').split('_')[0] #here to get 2 letters language
ui.run(port=8080,
       title='3CX CDR Server app',
       language=language,
       )