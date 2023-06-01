# -*- coding: UTF-8 -*-
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import date

metadata = SQLModel.metadata


class extensiontoqueuelink(SQLModel, table=True):
    extension_id: Optional[int] = Field(
        default=None, foreign_key="extensions.id", primary_key=True
    )
    queue_id: Optional[int] = Field(
        default=None, foreign_key="queues.id", primary_key=True
    )


class extensionsBase(SQLModel):
    extension: str = Field(index=True)
    name: str = Field(index=True)
    mail: str
    date_added: date = Field(default=date.today())
    date_out: Optional[date]
    out: bool = Field(default=False)


class extensions(extensionsBase, table=True):
    """
    Table listant les extensions(n° 3cx)
    """

    id: int = Field(default=None, primary_key=True)


class extensionsCreate(extensionsBase):
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