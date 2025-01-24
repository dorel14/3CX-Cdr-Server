from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EventTypeBase(BaseModel):
    name: str

class EventTypeCreate(EventTypeBase):
    pass

class EventTypeUpdate(EventTypeBase):
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

    class Config:
        orm_mode: True


