from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Time, Date, ForeignKey
from helpers.base import Base

class CallDataRecords(Base):
    __tablename__ = "call_data_records"

    id = Column(Integer, primary_key=True, nullable=False)
    historyid = Column(String, unique=True)
    callid = Column(String, unique=True)
    duration = Column(Time)
    time_start = Column(DateTime)
    time_answered = Column(DateTime)
    time_end = Column(DateTime)
    reason_terminated = Column(String)
    from_no = Column(String)
    to_no = Column(String)
    from_dn = Column(String)
    to_dn = Column(String)
    dial_no = Column(String)
    reason_changed = Column(String)
    final_number = Column(String)
    final_dn = Column(String)
    bill_code = Column(String)
    bill_rate = Column(Float)
    bill_cost = Column(Float)
    bill_name = Column(String)
    chain = Column(String)
    from_type = Column(String)
    to_type = Column(String)
    final_type = Column(String)
    from_dispname = Column(String)
    to_dispname = Column(String)
    final_dispname = Column(String)
    missed_queue_calls = Column(String)

class CallDataRecordsDetails(Base):
    __tablename__ = "call_data_records_details"

    id = Column(Integer, primary_key=True, nullable=False)
    cdr_historyid = Column(String, ForeignKey("call_data_records.historyid"), nullable=False)
    abandonned = Column(Boolean)
    handling_time_seconds = Column(Integer)
    waiting_time_seconds = Column(Integer)
    call_date = Column(Date)
    call_time = Column(Time)
    call_week = Column(Integer)
    day_of_week = Column(String)
    filename = Column(String)