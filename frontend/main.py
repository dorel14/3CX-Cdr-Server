# -*- coding: UTF-8 -*-

from pages.generals import theme
from pages import homepage 
from pages import extensions_view
from pages import events_view
from pages import queues_view
from fastapi import status
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

@app.get('/healthcheck', status_code=status.HTTP_200_OK, tags=["health"])
def perform_healthcheck():
    '''
    Simple route for the GitHub Actions to healthcheck on.
    More info is available at:
    https://github.com/akhileshns/heroku-deploy#health-check
    It basically sends a GET request to the route & hopes to get a "200"
    response code. Failing to return a 200 response code just enables
    the GitHub Actions to rollback to the last version the project was
    found in a "working condition". It acts as a last line of defense in
    case something goes south.
    Additionally, it also returns a JSON response in the form of:
    {
        'healtcheck': 'Everything OK!'
    }
    '''
    return {'healthcheck': 'Webapp OK!'}

language = os.environ.get('LOCALE_LANGUAGE').split('_')[0] #here to get 2 letters language

ui.run(host='0.0.0.0',
        port=8181,
        title='3CX CDR Server app',
        language=language,
        favicon="🚀",
        root_path="/webapp",
        )
