from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List



class ExtraEventBase(BaseModel):
    event_title: str
    event_start: datetime = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_added: datetime = datetime.now()
    date_modified: datetime = datetime.now()
    all_day: bool = False
    extensionslist : List[str] = []
    queueslist : List[str] = []

class ExtraEventCreate(ExtraEventBase):
    queues_ids: Optional[List[int]] = None
    extensions_ids: Optional[List[int]] = None
    pass

class ExtraEvent(ExtraEventBase):
    id: int
    queues_ids: Optional[List[int]]
    extensions_ids: Optional[List[int]]
    class Config:
        from_attributes = True

class ExtraEventUpdate(BaseModel):
    event_title: str
    event_start: Optional[datetime] = datetime.now()
    event_end: Optional[datetime] = None
    event_description: Optional[str] = None
    event_impact: Optional[str] = None
    date_modified: datetime = datetime.now()
    extensionslist : Optional[List[str]] = None
    queueslist : Optional[List[str]] = None
