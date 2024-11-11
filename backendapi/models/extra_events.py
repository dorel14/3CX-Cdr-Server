# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from helpers.base import Base

class ExtraEvents(Base):
    __tablename__ = "extra_events"

    id = Column(Integer, primary_key=True, nullable=False)
    event_title = Column(String)
    event_start = Column(DateTime, default=datetime.now())
    event_end = Column(DateTime, nullable=True)
    event_description = Column(String, nullable=True)
    event_impact = Column(String, nullable=True) 
    date_added = Column(DateTime, default=datetime.now())
    date_modified = Column(DateTime, default=datetime.now())
    all_day = Column(Boolean, default=False)