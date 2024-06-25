from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import Union, List


import os
import sys

sys.path.append(os.path.abspath("."))

from myhelpers.base import get_session
from myhelpers.logging import logger

from models.tab3cxcdr import (
    call_data_records,
    call_data_records_base,
    call_data_records_create,
    call_data_records_read,
    call_data_records_details,
    call_data_records_details_create,
    call_data_records_details_read
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
async def read_cdr(*,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    ):
    db_cdr=session.exec(select(call_data_records).offset(offset).limit(limit)).all()
    return db_cdr

@router.get("/cdr/{callid}", response_model=call_data_records_read, tags=["cdr"])
async def read_cdr_by_callid(*, session: Session = Depends(get_session), callid: str):
    db_cdr_by_cid = session.exec(select(call_data_records).where(call_data_records.callid==callid)).one_or_none()
    print(db_cdr_by_cid)
    if not db_cdr_by_cid:
        logger.info(f"callid {callid} non trouvée")
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_cid

@router.get("/cdr/historyid/{historyid}", response_model=call_data_records_read, tags=["cdr"])
async def read_cdr_by_historyid(*, session: Session = Depends(get_session), historyid: str):
    db_cdr_by_hid = session.exec(select(call_data_records).where(call_data_records.historyid==historyid)).one_or_none()
    print(db_cdr_by_hid)
    if not db_cdr_by_hid:
        logger.info(f"historyid {historyid} non trouvée")
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_hid

@router.post('/cdrdetails', response_model=call_data_records_details_read, tags=["cdr_details"])
async def create_cdr_details(*, session: Session=Depends(get_session), call_data_record_detail:call_data_records_details_create):
    db_cdr_detail=call_data_records_details.from_orm(call_data_record_detail)
    session.add(db_cdr_detail)
    session.commit()
    session.refresh(db_cdr_detail)
    return db_cdr_detail

@router.get('/cdrdetails', response_model=List[call_data_records_details_read], tags=["cdr_details"])
async def read_cdr_details(*,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    ):
    db_cdr_details=session.exec(select(call_data_records_details).offset(offset).limit(limit)).all()
    return db_cdr_details

@router.get("/cdrdetails/historyid/{historyid}", response_model=call_data_records_details_read, tags=["cdr_details"])
async def read_cdrdetails_by_historyid(*, session: Session = Depends(get_session), historyid: str):
    db_cdr_by_hid = session.exec(select(call_data_records_details).where(call_data_records_details.cdr_historyid==historyid)).one_or_none()
    print(db_cdr_by_hid)
    if not db_cdr_by_hid:
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_hid