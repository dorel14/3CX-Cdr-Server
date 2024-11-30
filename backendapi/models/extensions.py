# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String,  DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from ..helpers.base import Base

class Extensions(Base):
    __tablename__ = "extensions"

    id = Column(Integer, primary_key=True)
    extension = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    mail = Column(String(255), nullable=True, index=True)
    date_added = Column(DateTime, default=func.now())
    date_out = Column(DateTime, default=None, nullable=True)
    out = Column(Integer, default=False)
    date_modified = Column(DateTime, default=func.now())
    eventslist = relationship("ExtraEvents", secondary='ExtensionsEvents',back_populates="extensionslist")
    queueslist = relationship("Queues", secondary='Extensiontoqueuelink',back_populates="extensionslist")
    