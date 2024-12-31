# -*- coding: UTF-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from datetime import datetime



from ..helpers.base import Base

class QueuesEvents(Base):
    __tablename__ = "queues_events"
    id = Column(Integer, primary_key=True)
    queue_id = Column(Integer, ForeignKey('queues.id'), nullable=False)
    event_id = Column(Integer,ForeignKey('extraevents.id') ,nullable=False)
    date_added = Column(DateTime, default=datetime.now())
    date_modified = Column(DateTime, default=datetime.now())