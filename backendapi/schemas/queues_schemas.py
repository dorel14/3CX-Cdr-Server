from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QueueBase(BaseModel):
    queue: str
    queuename: str
    date_added: Optional[datetime] = datetime.now()
    date_modified: Optional[datetime] = datetime.now()

class QueueCreate(QueueBase):
    pass

class Queue(QueueBase):
    id: int

    class Config:
        orm_mode = True

class QueueUpdate(BaseModel):
    queue: Optional[str] = None
    queuename: Optional[str] = None
    date_modified: Optional[datetime] = datetime.now()