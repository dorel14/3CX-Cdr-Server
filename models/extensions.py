# -*- coding: UTF-8 -*-
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date, datetime

from models import queues

metadata = SQLModel.metadata


class extensiontoqueuelink(SQLModel, table=True):
    extension_id: Optional[int] = Field(
        default=None, foreign_key="extensions.id", primary_key=True, nullable=False
    )
    queue_id: Optional[int] = Field(
        default=None, foreign_key="queues.id", primary_key=True, nullable=False
    )


class extensionsBase(SQLModel):
    extension: str = Field(index=True, sa_column_kwargs={'unique': True})
    name: str = Field(index=True)
    mail: str
    date_added: Optional[datetime] = Field(default=datetime.now())
    date_out: Optional[date] =Field(default=None)
    out: Optional[bool] = Field(default=False)
    date_modified: Optional[datetime] = Field(default=datetime.now())
    
 

class extensions(extensionsBase, table=True):
    """
    Table listant les extensions(n° 3cx)
    """

    id: int = Field(default=None, primary_key=True,nullable=False)
    #queues: Optional[list["queues"]] = Relationship(back_populates="extensions", link_model=extensiontoqueuelink)  # type: ignore


class extensionsCreate(extensionsBase):
    date_added: Optional[datetime] = Field(default=datetime.now())
    
    pass


class extensionsRead(extensionsBase):
    id: int
    

class extensionUpdate(SQLModel):
    extension: Optional[str]=None
    name: Optional[str]=None 
    mail: Optional[str]=None
    date_added: Optional[date]=None
    date_out: Optional[date]=None
    out: Optional[bool]=False
    date_modified: Optional[datetime] = Field(default=datetime.now())
    