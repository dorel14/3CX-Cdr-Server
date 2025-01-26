from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import ValidationError
from datetime import datetime
from typing import List




from ..helpers.base import get_session
from ..helpers.logging import logger

from ..models.tab3cxcdr import (CallDataRecords as call_data_records, 
                                CallDataRecordsDetails as call_data_records_details
                                )
from ..schemas.tab3cxcdr_schemas import (
    CallDataRecordBase as call_data_records_read,
    CallDataRecordCreate as call_data_records_create,
    CallDataRecordDetailsBase as call_data_records_details_read,
    CallDataRecordDetailsCreate as call_data_records_details_create
)

router = APIRouter(prefix="/v1")

@router.post('/cdr', response_model=call_data_records_read, tags=["cdr"])
async def create_cdr(call_data_record:call_data_records_create,
                    session: AsyncSession = Depends(get_session), ):
    try:
        db_cdr=call_data_records(**call_data_record.dict())
        async with session as s:
            s.add(db_cdr)
            await s.commit()
            await s.refresh(db_cdr)
        logger.info(f"CDR created successfully with callid: {db_cdr.callid}")
        return db_cdr
    except Exception as e:
        logger.error(f"Error creating CDR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create CDR record")

@router.get('/cdr', response_model=List[call_data_records_read], tags=["cdr"])
async def read_cdr(*,
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    ):
    async with session as s:
        result = await s.execute(select(call_data_records).offset(offset).limit(limit))
        db_cdr=result.scalars().all()
    return db_cdr

@router.get("/cdr/{callid}", response_model=call_data_records_read, tags=["cdr"])
async def read_cdr_by_callid(callid: str,
                            session: AsyncSession = Depends(get_session), ):
    async with session as s:
        result  = await s.execute(select(call_data_records).where(call_data_records.callid==callid))
        db_cdr_by_cid = result.scalar_one_or_none()
    print(db_cdr_by_cid)
    if not db_cdr_by_cid:
        logger.info(f"callid {callid} non trouvée")
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_cid

@router.get("/cdr/historyid/{historyid}", response_model=call_data_records_read, tags=["cdr"])
async def read_cdr_by_historyid(historyid: str,
                                session: AsyncSession = Depends(get_session), ):
    async with session as s:
        result  = await s.execute(select(call_data_records).where(call_data_records.historyid==historyid))
        db_cdr_by_hid = result.scalar_one_or_none()
    print(db_cdr_by_hid)
    if not db_cdr_by_hid:
        logger.info(f"historyid {historyid} non trouvée")
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_hid

@router.get('/cdr/search', response_model=List[call_data_records_read], tags=["cdr"])
async def search_cdr(
    *,
    session: AsyncSession = Depends(get_session),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    limit: int = Query(default=100, lte=100)
):
    query = select(call_data_records)
    if start_date and end_date:
        query = query.where(
            call_data_records.timestart.between(start_date, end_date)
        )
    async with session as s:
        result = await s.execute(query.limit(limit))
    return result.scalars().all()


@router.post('/cdrdetails', response_model=call_data_records_details_read, tags=["cdr_details"])
async def create_cdr_details(call_data_record_detail:call_data_records_details_create,
                            session: AsyncSession=Depends(get_session), ):
    try:
        db_cdr_detail=call_data_records_details(**call_data_record_detail.dict())
        async with session as s:
            s.add(db_cdr_detail)
            await s.commit()
            await s.refresh(db_cdr_detail)
        return db_cdr_detail
    except Exception as e:
        logger.error(f"Error creating CDR details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create CDR details record")

@router.get('/cdrdetails', response_model=List[call_data_records_details_read], tags=["cdr_details"])
async def read_cdr_details(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    ):
    async with session as s:
        result = await s.execute(select(call_data_records_details).offset(offset).limit(limit))
        db_cdr_details=result.scalars().all()
    return db_cdr_details

@router.get("/cdrdetails/historyid/{historyid}", response_model=call_data_records_details_read, tags=["cdr_details"])
async def read_cdrdetails_by_historyid(historyid: str,
                                    session: AsyncSession = Depends(get_session), ):
    async with session as s:
        result  = await s.execute(select(call_data_records_details).where(call_data_records_details.cdr_historyid==historyid))
        db_cdr_by_hid = result.scalar_one_or_none()
    logger.info(db_cdr_by_hid)
    if not db_cdr_by_hid:
        raise HTTPException(status_code=404, detail="cdr non trouvée")
    return db_cdr_by_hid


@router.post("/cdr/validate", status_code=200, tags=["cdr"])
async def validate_cdr(cdr: call_data_records_create):
    try:
        #La validation est faites par pydantic
        return {"status":"valid"}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/cdrdatails/validate", status_code=200, tags=["cdr_details"])
async def validate_cdr_details(cdr_details: call_data_records_details_create):
    try:
        #Validation faite par Pydantic
        return {"status": "valid"}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/cdr", response_model=List[call_data_records_read], tags=["cdr"])
async def read_cdr(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    async with session as s:
        result = await s.execute(
            select(call_data_records_read)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

@router.get("/cdr/{cdr_id}", response_model=call_data_records_read, tags=["cdr"])
async def read_cdr_by_id(
    cdr_id: int,
    session: AsyncSession = Depends(get_session),
):
    async with session as s:
        result = await s.execute(
            select(call_data_records_read)
            .filter(call_data_records_read.id == cdr_id)
        )
        cdr = result.scalar_one_or_none()
        if cdr is None:
            raise HTTPException(status_code=404, detail="CDR not found")
        return cdr