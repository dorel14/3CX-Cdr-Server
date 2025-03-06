# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, ForeignKey
from ..helpers.base import Base

class EventsTypesEvents(Base):
    __tablename__ = "events_types_events"
    event_id = Column(Integer, ForeignKey('extraevents.id'), primary_key=True)
    event_type_id = Column(Integer, ForeignKey('events_types.id'), primary_key=True)