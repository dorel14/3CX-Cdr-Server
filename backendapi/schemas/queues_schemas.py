from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class QueueBase(BaseModel):
    queue: str
    queuename: str
    date_added: Optional[datetime] = datetime.now()
    date_modified: Optional[datetime] = datetime.now()

class QueueCreate(QueueBase):
    pass

class Queue(QueueBase):
    id: int
    extensionslist: Optional[List["Extension"]] = []

    class Config:
        from_attributes = True

class QueueUpdate(BaseModel):
    queue: Optional[str] = None
    queuename: Optional[str] = None
    date_modified: Optional[datetime] = datetime.now()

from .extensions_schemas import Extension  # noqa: E402
Queue.update_forward_refs()