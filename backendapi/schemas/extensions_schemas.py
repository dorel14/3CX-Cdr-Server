# -*- coding: UTF-8 -*-
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class ExtensionBase(BaseModel):
    extension: str
    name: str
    mail: str
    date_added: Optional[datetime] = datetime.now()
    date_out: Optional[date] = None
    out: Optional[bool] = False
    date_modified: Optional[datetime] = datetime.now()

class ExtensionCreate(ExtensionBase):
    pass

class Extension(ExtensionBase):
    id: int

    class Config:
        from_attributes = True

class ExtensionUpdate(BaseModel):
    extension: Optional[str] = None
    name: Optional[str] = None
    mail: Optional[str] = None
    date_added: Optional[date] = None
    date_out: Optional[date] = None
    out: Optional[bool] = False
    date_modified: Optional[datetime] = datetime.now()