# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..helpers.base import Base



class Queues(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, nullable=False)
    queue = Column(String)
    queuename = Column(String)
    date_added = Column(DateTime, default=datetime.now())
    date_modified = Column(DateTime, default=datetime.now())
