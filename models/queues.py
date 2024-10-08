# -*- coding: UTF-8 -*-
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
# from extensions import extensionsextensiontoqueuelink
metadata = SQLModel.metadata



class queueBase(SQLModel):
    queue: str
    queuename: str
    date_added: Optional[datetime] = Field(default=datetime.now())
    date_modified: Optional[datetime] = Field(default=datetime.now())


class queues(queueBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)


class queuesCreate(queueBase):
    date_added: Optional[datetime] = Field(default=datetime.now())
    pass

class queuesRead(queueBase):
    id: int

class queueUpdate(SQLModel):
    queue: Optional[str]=None
    queuename: Optional[str]=None
    date_modified: Optional[datetime] = Field(default=datetime.now())
