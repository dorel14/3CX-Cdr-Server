# -*- coding: UTF-8 -*-
from helpers.base import Base, DbSession
from sqlalchemy import Column, DateTime, Integer, String, Time


class call_data_records(Base):
    """
    Table de gestion des statistiques individuelles d'appels
    """
    __tablename__ = "call_data_records"

    id = Column(Integer, primary_key=True, autoincrement=True)

    historyid = Column(String, unique=True)  # - The ID you can use to link the call do the details
    callid = Column(String)  # - I'm guessing this is for something internal,not of use.
    duration = Column(Time, nullable=True)
    time_start = Column(DateTime, nullable=True)  # - Start of the call, timestamp field
    time_answered = Column(DateTime, nullable=True)  # - Answer time, timestamp field
    time_end = Column(DateTime, nullable=True)  # - End of the call, timestamp field
    reason_terminated = Column(String)
    from_no = Column(String)  # - If its direct then this is the same as CallerID, if its to a group the group number is shown here, also if the call goes through a call menu the number of it is shown here
    to_no = Column(String)
    from_dn = Column(String)
    to_dn = Column(String)
    dial_no = Column(String)
    reason_changed = Column(String)
    final_number = Column(String)
    final_dn = Column(String)
    bill_code = Column(String)
    bill_rate = Column(String)
    bill_cost = Column(String)
    bill_name = Column(String)
    chain = Column(String)

    def __init__(self, historyid, callid, duration, time_start, time_answered,
                 time_end, reason_terminated, from_no, to_no, from_dn, to_dn,
                 dial_no, reason_changed, final_number, final_dn, bill_code,
                 bill_rate, bill_cost,bill_name,
                 chain):
        self.historyid = historyid
        self.callid = callid
        self.duration = duration
        self.time_start = time_start
        self.time_answered = time_answered
        self.time_end = time_end
        self.reason_terminated = reason_terminated
        self.from_no = from_no
        self.to_no = to_no
        self.from_dn = from_dn
        self.to_dn = to_dn
        self.dial_no = dial_no
        self.reason_changed = reason_changed
        self.final_number = final_number
        self.final_dn = final_dn
        self.bill_code = bill_code
        self.bill_rate = bill_rate
        self.bill_cost = bill_cost
        self.bill_name = bill_name
        self.chain = chain
