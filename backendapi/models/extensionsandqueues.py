# -*- coding: UTF-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from datetime import datetime



from ..helpers.base import Base

class Extensiontoqueuelink(Base):
    __tablename__ = "extensiontoqueuelink"
    id = Column(Integer, primary_key=True)
    extension_id = Column(Integer, ForeignKey('extensions.id'), nullable=False)
    queue_id = Column(Integer, ForeignKey('queues.id'), nullable=False)
    date_added = Column(DateTime, default=datetime.now())
    date_modified = Column(DateTime, default=datetime.now())