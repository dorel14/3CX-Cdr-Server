from pydantic import BaseModel
from datetime import datetime
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


class ExtraEventCreate(BaseModel):
    event_title: str
    event_start: datetime = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_added: datetime = datetime.now()
    date_modified: datetime = datetime.now()
    all_day: bool = False
    queueslist: Optional[List[QueueId]] = []
    extensionslist: Optional[List[ExtensionId]] = []
    event_typeslist: Optional[List[EventTypesId]] = []
    pass

class ExtraEvent(ExtraEventBase):
    id: int
    queueslist: Optional[List['QueueBase']] = []
    extensionslist: Optional[List["ExtensionBase"]] = []
    eventtypeslist: Optional[List["EventTypeBase"]] = []
    class Config:
        from_attributes = True
class ExtraEventUpdate(BaseModel):
    event_title: str
    event_start: Optional[datetime] = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_modified: datetime = datetime.now()
    all_day: bool = False
    queueslist: Optional[List[QueueId]] = []
    extensionslist: Optional[List[ExtensionId]] = []
    event_typeslist: Optional[List[EventTypesId]] = []

from .queues_schemas import QueueBase  # noqa: E402
from .extensions_schemas import ExtensionBase  # noqa: E402
from .event_types_schemas import EventTypeBase  # noqa: E402
ExtraEvent.update_forward_refs()