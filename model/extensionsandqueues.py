# -*- coding: UTF-8 -*-
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import date


class extensiontoqueuelink(SQLModel, table=True):
    extension_id: Optional[int] = Field(
        default=None, foreign_key="extensions.id", primary_key=True
    )
    queue_id: Optional[int] = Field(
        default=None, foreign_key="queues.id", primary_key=True
    )


class extensions(SQLModel, table=True):
    """
    Table listant les extensions(n° 3cx)
    """

    id: int = Field(default=None,
                    primary_key=True)
    extension: str
    name: str
    mail: str
    date_added: date = Field(default=date.today())
    date_out: date
    out: bool
    queuelist: List["queues"] = Relationship(back_populates="extensions",
                                             link_model=extensiontoqueuelink)


class queues(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    queue: str
    queuename: str
    extensionslist: List["extensions"] = Relationship(back_populates="extensions",
                                                      link_model=extensiontoqueuelink)
