from pydantic import BaseModel

class settings(BaseModel):
    section:str
    key:str
    value:str