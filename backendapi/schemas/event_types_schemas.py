from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EventTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

class EventTypeCreate(EventTypeBase):
    pass

class EventTypeUpdate(EventTypeBase):
    description: Optional[str] = None
    color: Optional[str] = None
    date_modified: Optional[datetime] = None

class EventType(EventTypeBase):
    id: int
    date_added: Optional[datetime] = None
    date_modified: Optional[datetime] = None

    class Config:
        orm_mode: True

class EventTypeWithEvents(EventType):
    eventslist: List["ExtraEvent"] = []

class ExtraEvent(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

    class Config:
        orm_mode: True


