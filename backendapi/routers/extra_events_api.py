from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import List
from datetime import datetime


from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.extra_events import (
    extraEventsBase,
    extraEventsRead,
    extraEvents,
    extraEventsCreate,
    extraEventsUpdate,
)

router = APIRouter(prefix="/v1", tags=["extra_events"])

@router.post("/extra_events", response_model=extraEventsBase, tags=["extra_events"])
async def create_extra_events(*, session: Session = Depends(get_session), extra_event: extraEventsCreate):
    logger.info(extra_event)
    db_extra_events = extraEvents.model_validate(extra_event)
    session.add(db_extra_events)
    session.commit()
    session.refresh(db_extra_events)
    return db_extra_events

@router.get(
    "/extra_events", response_model=List[extraEventsRead], tags=["extra_events"]
)
async def read_extra_events(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_extra_events = session.exec(
        select(extraEvents).offset(offset).limit(limit)
    ).all()
    return db_extra_events

@router.get(
    "/extra_events/{extra_events_id}", response_model=extraEventsRead, tags=["extra_events"]
)
async def read_extra_event(
    *, session: Session = Depends(get_session), extra_events_id: int
):
    db_extra_events = session.get(extraEvents, extra_events_id)
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    return db_extra_events

@router.patch(
    "/extra_events/{extra_events_id}", response_model=extraEventsRead, tags=["extra_events"]
)
async def update_extra_events(
    *, session: Session = Depends(get_session), extra_events_id: int, ex_events: extraEventsUpdate
):

    db_events = session.get(extraEvents, extra_events_id)
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
    session.commit()
    session.refresh(db_events)
    return db_events

@router.delete(
    "/extra_events/{extra_events_id}", response_model=extraEventsRead, tags=["extra_events"]
)
async def delete_extra_events(
    *, session: Session = Depends(get_session), extra_events_id: int
):
    db_extra_events = session.get(extraEvents, extra_events_id)
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    session.delete(db_extra_events)
    session.commit()
    return db_extra_events