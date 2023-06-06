from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import Union, List

import os
import sys

sys.path.append(os.path.abspath("."))

from myhelpers.base import get_session

from models.tab3cxcdr import (
    call_data_records,
    call_data_records_base,
    call_data_records_create,
    call_data_records_read
)
router = APIRouter(prefix="/api/v1")

@router.post('/cdr', response_model=call_data_records_read, tags=["cdr"])
async def create_cdr(*, session: Session = Depends(get_session), call_data_record:call_data_records_create):
    db_cdr=call_data_records.from_orm(call_data_record)
    session.add(db_cdr)
    session.commit()
    session.refresh(db_cdr)
    return db_cdr

@router.get('/cdr', response_model=List[call_data_records_read], tags=["cdr"])
async def read_cdr(    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    ):
    db_cdr=session.exec(select(call_data_records).offset(offset).limit(limit)).all()
    return db_cdr