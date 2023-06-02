# -*- coding: UTF-8 -*-
from fastapi import FastAPI, status
from typing import Union
from .routers import extensions_api

app = FastAPI()
app.include_router(extensions_api.router) #permet d'ajouter les routes d'un fichier externe

@app.get('/')
async def root():
    return{'message':'Hello World'}

@app.get('/healthcheck', status_code=status.HTTP_200_OK)
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
    return {'healthcheck': 'Everything OK!'}
