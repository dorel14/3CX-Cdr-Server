# -*- coding: UTF-8 -*-
from sqlmodel import Field, SQLModel
metadata = SQLModel.metadata

class queueBase(SQLModel):
    queue: str
    queuename: str


class queues(queueBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)

class queuesCreate(queueBase):
    pass

