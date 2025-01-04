# -*- coding: UTF-8 -*-
from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

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
    queueslist: Optional[List['QueueBase']] = []

    class Config:
        from_attributes = True
class QueueId(BaseModel):
    id: int
class ExtensionUpdate(BaseModel):
    extension: Optional[str] = None
    name: Optional[str] = None
    mail: Optional[str] = None
    date_added: Optional[date] = None
    date_out: Optional[date] = None
    out: Optional[bool] = False
    date_modified: Optional[datetime] = datetime.now()
    queues: Optional[List[QueueId]] = []

from .queues_schemas import Queue  # noqa: E402
from .queues_schemas import QueueBase  # noqa: E402
Extension.update_forward_refs()