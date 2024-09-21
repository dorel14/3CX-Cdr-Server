# -*- coding: UTF-8 -*-
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath("."))
#from models import extensions
#from models.extensions import extensiontoqueuelink

metadata = SQLModel.metadata



class queueBase(SQLModel):
    queue: str
    queuename: str
    date_added: Optional[datetime] = Field(default=datetime.now())
    date_modified: Optional[datetime] = Field(default=datetime.now())
    

class queues(queueBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    #extensions: Optional[list["extensions"]] = Relationship(back_populates="queues", link_model=extensiontoqueuelink)  # type: ignore


class queuesCreate(queueBase):
    date_added: Optional[datetime] = Field(default=datetime.now())    
    pass

class queuesRead(queueBase):
    id: int

class queueUpdate(SQLModel):
    queue: Optional[str]=None
    queuename: Optional[str]=None
    date_modified: Optional[datetime] = Field(default=datetime.now())

