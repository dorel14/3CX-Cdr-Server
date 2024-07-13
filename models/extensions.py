# -*- coding: UTF-8 -*-
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import date

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
    date_added: Optional[date] = Field(default=date.today())
    date_out: Optional[date] =Field(default=None)
    out: Optional[bool] = Field(default=False)


class extensions(extensionsBase, table=True):
    """
    Table listant les extensions(n° 3cx)
    """

    id: int = Field(default=None, primary_key=True,nullable=False)


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