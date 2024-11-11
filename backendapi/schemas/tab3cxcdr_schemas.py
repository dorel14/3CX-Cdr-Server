from pydantic import BaseModel
from datetime import datetime, time, date
from typing import Optional

class CallDataRecordBase(BaseModel):
    historyid: str
    callid: str
    duration: Optional[time]
    time_start: Optional[datetime]
    time_answered: Optional[datetime]
    time_end: Optional[datetime]
    reason_terminated: Optional[str]
    from_no: Optional[str]
    to_no: Optional[str]
    from_dn: Optional[str]
    to_dn: Optional[str]
    dial_no: Optional[str]
    reason_changed: Optional[str]
    final_number: Optional[str]
    final_dn: Optional[str]
    bill_code: Optional[str]
    bill_rate: Optional[float]
    bill_cost: Optional[float]
    bill_name: Optional[str]
    chain: Optional[str]
    from_type: Optional[str]
    to_type: Optional[str]
    final_type: Optional[str]
    from_dispname: Optional[str]
    to_dispname: Optional[str]
    final_dispname: Optional[str]
    missed_queue_calls: Optional[str]

class CallDataRecordCreate(CallDataRecordBase):
    pass

class CallDataRecord(CallDataRecordBase):
    id: int

    class Config:
        orm_mode = True

class CallDataRecordDetailsBase(BaseModel):
    cdr_historyid: str
    abandonned: bool
    handling_time_seconds: int
    waiting_time_seconds: int
    call_date: date
    call_time: time
    call_week: int
    day_of_week: str
    filename: Optional[str]

class CallDataRecordDetailsCreate(CallDataRecordDetailsBase):
    pass

class CallDataRecordDetails(CallDataRecordDetailsBase):
    id: int

    class Config:
        orm_mode = True