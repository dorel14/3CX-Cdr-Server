from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from typing import List
from datetime import datetime


from ..helpers.base import get_session
from ..helpers.logging import logger

from ..models.extra_events import ExtraEvents
from ..models.extensions import Extensions
from ..models.queues import Queues
from ..models.extensions_events import ExtensionsEvents
from ..models.queues_events import QueuesEvents

from ..schemas.events_schemas import ExtraEventBase, ExtraEventCreate, ExtraEventUpdate

router = APIRouter(prefix="/v1", tags=["extra_events"])

@router.post("/extra_events/", response_model=ExtraEventBase, tags=["extra_events"])
async def create_event(
    event: ExtraEventCreate,
    session: AsyncSession = Depends(get_session)
):
    # Création de l'événement
    db_event = ExtraEvents(**event.dict(exclude={'queues', 'extensions'}))
    session.add(db_event)
    await session.flush()  # Pour obtenir l'ID de l'événement

    # Création des liaisons avec les queues
    if event.queues:
        for queue_id in event.queues:
            queue_event = QueuesEvents(
                queue_id=queue_id,
                event_id=db_event.id
            )
            session.add(queue_event)

    # Création des liaisons avec les extensions
    if event.extensions:
        for extension_id in event.extensions:
            extension_event = ExtensionsEvents(
                extension_id=extension_id,
                event_id=db_event.id
            )
            session.add(extension_event)

    await session.commit()
    await session.refresh(db_event)
    return db_event

@router.get(
    "/extra_events", response_model=List[ExtraEventBase], tags=["extra_events"]
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
    "/extra_events/{extra_events_id}", response_model=ExtraEventBase, tags=["extra_events"]
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


@router.patch("/extra_events/{extra_events_id}", response_model=ExtraEventBase, tags=["extra_events"])
async def update_extra_events(
    extra_events_id: int, 
    ex_events: ExtraEventUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(ExtraEvents).where(ExtraEvents.id == extra_events_id))
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
        # Remove existing relationships
        await session.execute(
            delete(ExtensionsEvents).where(ExtensionsEvents.event_id == extra_events_id)
        )
        # Create new relationships
        extensions = await session.execute(
            select(Extensions).where(Extensions.extension.in_(ex_events.extensionslist))
        )
        for ext in extensions.scalars().all():
            ext_event = ExtensionsEvents(
                extension_id=ext.id,
                event_id=extra_events_id
            )
            session.add(ext_event)
    
    # Update queues relationships
    if ex_events.queueslist is not None:
        # Remove existing relationships
        await session.execute(
            delete(QueuesEvents).where(QueuesEvents.event_id == extra_events_id)
        )
        # Create new relationships
        queues = await session.execute(
            select(Queues).where(Queues.queue.in_(ex_events.queueslist))
        )
        for queue in queues.scalars().all():
            queue_event = QueuesEvents(
                queue_id=queue.id,
                event_id=extra_events_id
            )
            session.add(queue_event)
    
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