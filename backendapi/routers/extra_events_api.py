from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from typing import List
from datetime import datetime


from ..helpers.base import get_session

from ..models.extra_events import ExtraEvents
from ..models.extensions_events import ExtensionsEvents
from ..models.queues_events import QueuesEvents

from ..schemas.events_schemas import ExtraEventBase, ExtraEventCreate, ExtraEventUpdate, ExtraEvent

router = APIRouter(prefix="/v1", tags=["extra_events"])

@router.post("/extra_events", response_model=ExtraEventBase, tags=["extra_events"])
async def create_event(
    event: ExtraEventCreate,
    session: AsyncSession = Depends(get_session)
):
    # Création de l'événement
    db_event = ExtraEvents(
        event_title=event.event_title,
        event_start=event.event_start,
        event_end=event.event_end,
        event_description=event.event_description,
        event_impact=event.event_impact,
        all_day=event.all_day        
    )
    session.add(db_event)
    await session.flush()  # Pour obtenir l'ID de l'événement

    # Création des liaisons avec les queues
    if event.queueslist:
        for queue in event.queueslist:
            queue_event = QueuesEvents(
                queue_id=queue.id,
                event_id=db_event.id
            )
            session.add(queue_event)

    # Création des liaisons avec les extensions
    if event.extensionslist:
        for extension in event.extensionslist:
            extension_event = ExtensionsEvents(
                extension_id=extension.id,
                event_id=db_event.id
            )
            session.add(extension_event)

    await session.commit()
    await session.refresh(db_event)
    return db_event

@router.get(
    "/extra_events", response_model=List[ExtraEvent], tags=["extra_events"]
)
async def read_extra_events(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    result = await session.execute(
        select(ExtraEvents)
        .options(selectinload(ExtraEvents.extensionslist))
        .options(selectinload(ExtraEvents.queueslist))
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()

@router.get(
    "/extra_events/{extra_events_id}", response_model=ExtraEvent, tags=["extra_events"]
)
async def read_extra_event(
    extra_events_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ExtraEvents)
        .options(selectinload(ExtraEvents.extensionslist))
        .options(selectinload(ExtraEvents.queueslist))
        .where(ExtraEvents.id == extra_events_id)
    )
    db_extra_events = result.scalar_one_or_none()
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    return db_extra_events


@router.patch("/extra_events/{extra_events_id}", response_model=ExtraEvent, tags=["extra_events"])
async def update_extra_events(
    extra_events_id: int, 
    ex_events: ExtraEventUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ExtraEvents)
        .options(selectinload(ExtraEvents.extensionslist))
        .options(selectinload(ExtraEvents.queueslist))
        .where(ExtraEvents.id == extra_events_id)
        )
    db_events = result.scalar_one_or_none()
    if not db_events:
        raise HTTPException(status_code=404, detail="Event not found")

    events_data = ex_events.dict(exclude_unset=True, exclude={'extensionslist', 'queueslist'})
    events_data["date_modified"] = datetime.now()
    
    # Update basic fields
    for key, value in events_data.items():
        setattr(db_events, key, value)
    
    # Update extensions relationships
    if ex_events.extensionslist is not None:
        # Get existing extension IDs
        existing_ext_ids = {ext.id for ext in db_events.extensionslist}
        # Add new extensions while keeping existing ones
        for ext in ex_events.extensionslist:
            if ext.id not in existing_ext_ids:
                ext_event = ExtensionsEvents(
                    extension_id=ext.id,
                    event_id=extra_events_id
                )
                session.add(ext_event)
    
    # Update queues relationships
    if ex_events.queueslist is not None:
        # Get existing queue IDs
        existing_queue_ids = {queue.id for queue in db_events.queueslist}
        # Add new queues while keeping existing ones
        for queue in ex_events.queueslist:
            if queue.id not in existing_queue_ids:
                queue_event = QueuesEvents(
                    queue_id=queue.id,
                    event_id=extra_events_id
                )
                session.add(queue_event)
    
    await session.commit()
    await session.refresh(db_events)
    return db_events

@router.delete(
    "/extra_events/{extra_events_id}", response_model=ExtraEvent, tags=["extra_events"]
)
async def delete_extra_events(
    extra_events_id: int,
    session: AsyncSession = Depends(get_session), 
):
    # First delete all related records in junction tables
    await session.execute(
        delete(ExtensionsEvents).where(ExtensionsEvents.event_id == extra_events_id)
    )
    await session.execute(
        delete(QueuesEvents).where(QueuesEvents.event_id == extra_events_id)
    )
    
    # Then delete the event itself
    result = await session.execute(select(ExtraEvents).where(ExtraEvents.id == extra_events_id))
    db_extra_events = result.scalar_one_or_none()
    if not db_extra_events:
        raise HTTPException(status_code=404, detail="extra_events not found")
    
    await session.delete(db_extra_events)
    await session.commit()
    return db_extra_events


@router.delete("/extra_events/{event_id}/queue/{queue_id}", tags=["extra_events"])
async def delete_queue_from_event(
    event_id: int,
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    await session.execute(
        delete(QueuesEvents).where(
            QueuesEvents.event_id == event_id,
            QueuesEvents.queue_id == queue_id
        )
    )
    await session.commit()
    return {"status": "success"}

@router.delete("/extra_events/{event_id}/extension/{extension_id}", tags=["extra_events"])
async def delete_extension_from_event(
    event_id: int,
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    await session.execute(
        delete(ExtensionsEvents).where(
            ExtensionsEvents.event_id == event_id,
            ExtensionsEvents.extension_id == extension_id
        )
    )
    await session.commit()
    return {"status": "success"}