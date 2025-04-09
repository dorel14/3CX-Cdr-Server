from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from backendapi.models import extensions


class QueueBase(BaseModel):
    id: int
    queue: str
    queuename: str
    date_added: Optional[datetime] = datetime.now()
    date_modified: Optional[datetime] = datetime.now()

class QueueCreate(BaseModel):
    queue: str
    queuename: str
    date_added: Optional[datetime] = datetime.now()
    date_modified: Optional[datetime] = datetime.now()
    extensionslist: Optional[List["ExtensionsId"]] = []

class Queue(QueueBase):
    id: int
    extensionslist: Optional[List["ExtensionBase"]] = []

    class Config:
        from_attributes = True

class ExtensionsId(BaseModel):
    id: int

class QueueUpdate(BaseModel):
    queue: Optional[str] = None
    queuename: Optional[str] = None
    extensionslist: Optional[List[ExtensionsId]] = []
    date_modified: Optional[datetime] = datetime.now()

from .extensions_schemas import ExtensionBase  # noqa: E402
Queue.update_forward_refs()