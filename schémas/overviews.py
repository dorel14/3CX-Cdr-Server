# -*- coding: UTF-8 -*-
from pydantic import BaseModel, Field, Dict


class Overview(BaseModel):
    total_calls: int
    total_duration: float
    average_duration: float
    calls_by_type: Dict[str, int]
    calls_by_date: Dict[str, int]