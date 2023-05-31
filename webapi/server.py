# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from typing import Union
from .routers import extensions_api

app = FastAPI()
app.include_router(extensions_api.router) #permet d'ajouter les routes d'un fichier externe

@app.get('/')
async def root():
    return{'message':'Hello World'}
