
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime


from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.queues import Queues

from ..schemas.queues_schemas import Queue, QueueCreate, QueueUpdate

router = APIRouter(prefix="/v1", tags=["queues"])

@router.post("/queues", response_model=Queue, tags=["queues"])
async def create_queues(
    queue: QueueCreate,
    session: AsyncSession = Depends(get_session)    
):
    logger.info(queue)
    db_queues = Queues(**queue.dict())
    session.add(db_queues)
    await session.commit()
    await session.refresh(db_queues)
    return db_queues

@router.get("/queues", response_model=List[Queue], tags=["queues"])
async def read_queues(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_queues = await session.execute(select(Queues)
                                    .options(selectinload(Queues.extensionslist))
                                    .offset(offset)
                                    .limit(limit))
    return db_queues.scalars().all()

@router.get("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def read_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session)
    ):
    result = await session.execute(select(Queues).filter(Queues.id==queue_id))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/byname/{queue}", response_model=Queue, tags=["queues"])
async def read_queue_by_name(
    queue: str,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Queues).where(Queues.queuename == queue))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/bynumber/{queue}", response_model=Queue, tags=["queues"])
async def read_queue_by_number(
    queue: str,
    session: AsyncSession = Depends(get_session), ):

    result  = await session.execute(select(Queues).where(Queues.queue == queue))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue


router.delete("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def delete_queue(*, session: AsyncSession = Depends(get_session), queue_id: int):
    resultqueue = await session.execute(select(Queues).filter(Queues.id == queue_id))
    db_queue = resultqueue.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    await session.delete(db_queue)
    await session.commit()
    return db_queue

@router.patch("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def update_queue(
    queue_id: int,
    queue: QueueUpdate,
    session: AsyncSession = Depends(get_session),
    ):
    result  =  await session.execute(select(Queues).filter(Queues.id == queue_id))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    logger.info(queue)
    queue_data = queue.dict(exclude_unset=True)
    queue_data['date_modified'] = datetime.now()
    for key, value in queue_data.items():
        setattr(db_queue, key, value)
    session.add(db_queue)
    session.commit()
    session.refresh(db_queue)
    return db_queue

