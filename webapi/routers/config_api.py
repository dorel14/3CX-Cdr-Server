from fastapi import APIRouter
from typing import Union
import json
from helpers.config import Config, configFile
from model.config import settings

router = APIRouter(
    prefix='/config',
    tags=["settings"]
)

@router.get('/sections')
async def read_sections():
    sections = Config.sections()
    return json.dumps({'sections' : sections})

@router.get('/{section}/{cle}', tags=["settings"])
async def read_config(section:str, cle:str, q: Union[str, None] = None, short: bool = False):
    return {'config': Config.get(section=section,
                                 option=cle)}

@router.post('/', tags=["settings"])
async def write_config(settings:settings):
    if settings.section not in Config.sections():
        Config.add_section(settings.section)
    Config.set(settings.section,
               settings.key,
               settings.value)
    Config.write(open(configFile, 'w'))
    return settings