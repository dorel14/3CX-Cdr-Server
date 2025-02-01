from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..models.event_types import EventsTypes
from ..schemas.event_types_schemas import EventType, EventTypeCreate, EventTypeUpdate
from ..helpers.base import get_session


router = APIRouter(prefix="/v1", tags=["event_types"])

@router.post("/event_types/", response_model=EventType, tags=["event_types"])
async def create_event_type(event_type: EventTypeCreate, session: AsyncSession = Depends(get_session)):
    async with session as s:
        new_event_type = EventsTypes(**event_type.dict())
        s.add(new_event_type)
        await s.commit()
        await s.refresh(new_event_type)
        
    return new_event_type

@router.get("/event_types/{event_type_id}", response_model=EventType, tags=["event_types"])
async def read_event_type(event_type_id: int, session: AsyncSession = Depends(get_session)):
    async with session as s:
        result = await s.execute(select(EventsTypes).filter(EventsTypes.id == event_type_id))
        event_type = result.scalar_one_or_none()
        if event_type is None:
            raise HTTPException(status_code=404, detail="Event type not found")
    return event_type

@router.get("/event_types/by_name/{event_type_name}", response_model=EventType, tags=["event_types"])
async def read_event_type_by_name(event_type_name: str, session: AsyncSession = Depends(get_session)):
    async with session as s:
        result = await s.execute(select(EventsTypes).filter(EventsTypes.name == event_type_name))
        event_type = result.scalar_one_or_none()
        if event_type is None:
            raise HTTPException(status_code=404, detail="Event type not found")
    return event_type

@router.get("/event_types", response_model=List[EventType], tags=["event_types"])
async def read_event_types(session: AsyncSession = Depends(get_session)):
    async with session as s:
        result = await s.execute(select(EventsTypes))
        event_types = result.scalars().all()
    return event_types

@router.patch("/event_types/{event_type_id}", response_model=EventType, tags=["event_types"])
async def update_event_type(event_type_id: int, event_type: EventTypeUpdate, session: AsyncSession = Depends(get_session)):
    async with session as s:
        result = await s.execute(select(EventsTypes).filter(EventsTypes.id == event_type_id))
        db_event_type = result.scalar_one_or_none()
        if db_event_type is None:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        update_data = event_type.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event_type, key, value)
        
        s.add(db_event_type)
        await s.commit()
        await s.refresh(db_event_type)
        
    return db_event_type

@router.delete("/event_types/{event_type_id}", response_model=EventType, tags=["event_types"])
async def delete_event_type(event_type_id: int, session: AsyncSession = Depends(get_session)):
    async with session as s:
        result = await s.execute(select(EventsTypes).filter(EventsTypes.id == event_type_id))
        db_event_type = result.scalar_one_or_none()
        if db_event_type is None:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        await s.delete(instance=db_event_type)
        await s.commit()
        

    return db_event_type
