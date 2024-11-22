from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import List
from datetime import datetime


from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.extra_events import ExtraEvents
from ..schemas.events_schemas import ExtraEventBase, ExtraEventCreate, ExtraEventUpdate

router = APIRouter(prefix="/v1", tags=["extra_events"])

@router.post("/extra_events", response_model=ExtraEventBase, tags=["extra_events"])
async def create_extra_events(
    extra_event: ExtraEventCreate,
    session: AsyncSession = Depends(get_session)):

    logger.info(extra_event)
    db_extra_events = ExtraEvents(**extra_event.dict())
    session.add(db_extra_events)
    await session.commit()
    await session.refresh(db_extra_events)
    return db_extra_events

@router.get(
    "/extra_events", response_model=List[ExtraEventBase], tags=["extra_events"]
)
async def read_extra_events(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_extra_events = await session.execute(select(ExtraEvents).offset(offset).limit(limit))
    return db_extra_events.scalars().all()

@router.get(
    "/extra_events/{extra_events_id}", response_model=ExtraEventBase, tags=["extra_events"]
)
async def read_extra_event(
    extra_events_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(ExtraEvents).where(ExtraEvents.id == extra_events_id))
    db_extra_events = result.scalar_one_or_none()
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    return db_extra_events

@router.patch(
    "/extra_events/{extra_events_id}", response_model=ExtraEventBase, tags=["extra_events"]
)
async def update_extra_events(
    extra_events_id: int, 
    ex_events: ExtraEventUpdate,
    session: AsyncSession = Depends(get_session),
):

    result = await session.execute(select(ExtraEvents).where(ExtraEvents.id == extra_events_id))
    db_events = result.scalar_one_or_none()
    if not db_events:
        raise HTTPException(status_code=404, detail="Evénement non trouvée")
    logger.info(f'db_events: {db_events}')
    logger.info(f' Event: {ex_events}')
    events_data = ex_events.dict(exclude_unset=True)
    print(f'extensiondata: {events_data}')    
    events_data["date_modified"] = datetime.now()
    for key, value in events_data.items():
        setattr(db_events, key, value)
    session.add(db_events)
    await session.commit()
    await session.refresh(db_events)
    return db_events

@router.delete(
    "/extra_events/{extra_events_id}", response_model=ExtraEventBase, tags=["extra_events"]
)
async def delete_extra_events(
    extra_events_id: int,
    session: AsyncSession = Depends(get_session), 
):
    result = await session.execute(select(ExtraEvents).where(ExtraEvents.id == extra_events_id))
    db_extra_events = result.scalar_one_or_none()
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    await session.delete(db_extra_events)
    await session.commit()
    return db_extra_events