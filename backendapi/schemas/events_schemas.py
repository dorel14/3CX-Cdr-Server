from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class QueueId(BaseModel):
    id: int

class ExtensionId(BaseModel):
    id:int

class EventTypesId(BaseModel):
    id: int

class ExtraEventBase(BaseModel):
    id: int
    event_title: str
    event_start: datetime = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None    
    date_added: datetime = datetime.now()
    date_modified: datetime = datetime.now()
    all_day: bool = False
    recurrence_rule: Optional[str] = None
    exdate:Optional[List[datetime]] = []

class ExtraEventCreate(BaseModel):
    event_title: str
    event_start: datetime = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_added: datetime = datetime.now()
    date_modified: datetime = datetime.now()
    all_day: bool = False
    recurrence_rule: Optional[str] = None
    exdate:Optional[List[datetime]] = []
    queueslist: Optional[List[QueueId]] = []
    extensionslist: Optional[List[ExtensionId]] = []
    eventtypeslist: Optional[List[EventTypesId]] = []
    pass

class ExtraEvent(ExtraEventBase):
    id: int
    queueslist: Optional[List['QueueBase']] = []
    extensionslist: Optional[List["ExtensionBase"]] = []
    eventtypeslist: Optional[List["EventType"]] = []
    class Config:
        from_attributes = True
class ExtraEventUpdate(BaseModel):
    event_title: Optional[str]= None
    event_start: Optional[datetime] = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_modified: datetime = datetime.now()
    all_day: bool = False
    recurrence_rule: Optional[str] = None
    exdate:Optional[List[datetime]] = []
    queueslist: Optional[List[QueueId]] = []
    extensionslist: Optional[List[ExtensionId]] = []
    eventtypeslist: Optional[List[EventTypesId]] = []

from .queues_schemas import QueueBase  # noqa: E402
from .extensions_schemas import ExtensionBase  # noqa: E402
from .event_types_schemas import EventType  # noqa: E402
ExtraEvent.update_forward_refs()