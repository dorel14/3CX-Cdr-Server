# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String,  DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


from ..helpers.base import Base


class EventsTypes(Base):
    __tablename__ = "events_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(255), nullable=True)
    date_added = Column(DateTime, default=func.now())
    date_modified = Column(DateTime, default=func.now())
    eventslist = relationship("ExtraEvents",
                            secondary="events_types_events",
                            back_populates="eventtypeslist")
