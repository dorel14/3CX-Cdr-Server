# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime



from ..helpers.base import Base

class ExtraEvents(Base):
    __tablename__ = "extraevents"

    id = Column(Integer, primary_key=True, nullable=False)
    event_title = Column(String)
    event_start = Column(DateTime, default=datetime.now())
    event_end = Column(DateTime, nullable=True)
    event_description = Column(String, nullable=True)
    event_impact = Column(String, nullable=False, default="0") 
    date_added = Column(DateTime, default=datetime.now())
    date_modified = Column(DateTime, default=datetime.now())
    all_day = Column(Boolean, default=False)
    extensionslist = relationship("Extensions",
                                secondary="extensions_events",
                                back_populates="eventslist")
    queueslist = relationship("Queues",
                            secondary="queues_events",
                            back_populates="eventslist")
