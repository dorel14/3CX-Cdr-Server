# -*- coding: UTF-8 -*-
from sqlmodel import Field, SQLModel
from typing import Optional
# from extensions import extensionsextensiontoqueuelink
metadata = SQLModel.metadata



class queueBase(SQLModel):
    queue: str
    queuename: str


class queues(queueBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)


class queuesCreate(queueBase):
    pass

class queuesRead(queueBase):
    id: int

class queueUpdate(SQLModel):
    queue: Optional[str]=None
    queuename: Optional[str]=None 
