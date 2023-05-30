from fastapi import FastAPI
from typing import Union
from .routers import extensions_api

app = FastAPI()
app.include_router(extensions_api.router) #permet d'ajouter les routes d'un fichier externe

@app.get('/')
async def root():
    return{'message':'Hello World'}




@app.get('/extension/{extension_id}')
async def read_extension(extension_id:int, q: Union[str, None] = None):
    return {'extension_id': extension_id, 'q':q}