# -*- coding: UTF-8 -*-
from email.policy import default
from typing import List, Optional
from altair import Column
from click import DateTime
from sqlalchemy import Nullable
from sqlmodel import Field, SQLModel
from datetime import datetime, time, date
import pytz
import os
metadata = SQLModel.metadata


class CustomDatetime(datetime):
    """
    Custom datetime type for SQLModel
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, field):
        if isinstance(v, str):
            try:
                return cls.strptime(v, "%Y/%m/%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"{field.name} is not a valid datetime string")
        return v


class call_data_records_base(SQLModel):
    historyid: str = Field(sa_column_kwargs={'unique': True})  # - The ID you can use to link the call do the details
    callid: str = Field(sa_column_kwargs={'unique': True}) # - I'm guessing this is for something internal,not of use.
    duration: Optional[time] = None
    time_start: CustomDatetime = Field(default=None, sa_column_kwargs={"nullable": True})  # - Start of the call, timestamp field
    time_answered: CustomDatetime = Field(default=None, sa_column_kwargs={"nullable": True}) # Answer time, timestamp field
    time_end: CustomDatetime = Field(default=None, sa_column_kwargs={"nullable": True})  # - End of the call, timestamp field
    reason_terminated: Optional[str] = None
    from_no: Optional[str] = None # - If its direct then this is the same as CallerID, if its to a group the group number is shown here, also if the call goes through a call menu the number of it is shown here
    to_no: Optional[str] = None
    from_dn: Optional[str] = None
    to_dn: Optional[str] = None
    dial_no: Optional[str] = None
    reason_changed: Optional[str] = None
    final_number: Optional[str] = None
    final_dn: Optional[str] = None
    bill_code: Optional[str] = None
    bill_rate: Optional[float] = None
    bill_cost: Optional[float] = None
    bill_name: Optional[str] = None
    chain: Optional[str] = None
    from_type: Optional[str] = None
    to_type: Optional[str] = None
    final_type: Optional[str] = None
    from_dispname: Optional[str] = None
    to_dispname: Optional[str] = None
    final_dispname: Optional[str] = None
    missed_queue_calls: Optional[str] = None  # A list of queue agents that were polled during a queue call that didn’t answer the call

class call_data_records(call_data_records_base, table=True):
    """
    Table de gestion des statistiques individuelles d'appels
    """
    id: int = Field(default=None, primary_key=True, nullable=False)

class call_data_records_read(call_data_records_base):
    id:int
    

class call_data_records_create(call_data_records_base):
    pass




class call_data_records_details_base(SQLModel):
    cdr_historyid: Optional[str] = Field(default=None,
                                         foreign_key="call_data_records.historyid",
                                         nullable=False)
    abandonned: bool
    handling_time_seconds: int
    waiting_time_seconds: int
    call_date: date
    call_time: time
    call_week: int
    day_of_week: str
    filename:Optional[str]
    

class call_data_records_details(call_data_records_details_base, table=True):
        id: int = Field(default=None,
                    primary_key=True,
                    nullable=False)

class call_data_records_details_read(call_data_records_details_base):
     id:int

class call_data_records_details_create(call_data_records_details_base):
     pass






