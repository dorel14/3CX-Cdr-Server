from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.queues import Queues
from ..models.extensions import Extensions
from ..models.extensionsandqueues import Extensiontoqueuelink
from ..schemas.queues_schemas import Queue, QueueCreate, QueueUpdate

router = APIRouter(prefix="/v1", tags=["queues"])

@router.post("/queues", response_model=Queue, tags=["queues"])
async def create_queues(
    queue: QueueCreate,
    session: AsyncSession = Depends(get_session)    
):
    logger.info(queue)
    queue_data = queue.dict(exclude={"extensionslist"})
    db_queues = Queues(**queue_data)
    session.add(db_queues)
    await session.flush()
    created_id = db_queues.id
    
    # Add extensions links
    if queue.extensionslist:
        for ext in queue.extensionslist:
            link = Extensiontoqueuelink(queue_id=created_id, extension_id=ext.id)
            session.add(link)
    
    await session.commit()
    
    # Get fresh queue data with relationships
    stmt = select(Queues).options(selectinload(Queues.extensionslist)).filter(Queues.id == created_id)
    result = await session.execute(stmt)
    db_queue = result.unique().scalar_one()
    
    return db_queue

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
    result = await session.execute(
        select(Queues)
        .options(selectinload(Queues.extensionslist))
        .filter(Queues.id == queue_id)
    )
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/byname/{queuename}", response_model=Queue, tags=["queues"])
async def read_queue_by_name(
    queuename: str,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Queues)
                                .options(selectinload(Queues.extensionslist))
                                .where(Queues.queuename == queuename))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/bynumber/{queue}", response_model=Queue, tags=["queues"])
async def read_queue_by_number(
    queue: str,
    session: AsyncSession = Depends(get_session), ):

    result  = await session.execute(select(Queues)
                                    .options(selectinload(Queues.extensionslist))
                                    .where(Queues.queue == queue))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.delete("/queues/{queue_id}", response_model=Queue, tags=["queues"])
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
    result  =  await session.execute(select(Queues)
                                    .options(selectinload(Queues.extensionslist))
                                    .filter(Queues.id == queue_id))
    db_queue = result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    logger.info(queue)
    queue_data = queue.dict(exclude_unset=True)
    queue_data['date_modified'] = datetime.now()
    
    # Update queue attributes
    for key, value in queue_data.items():
        if key != 'extensionslist':
            setattr(db_queue, key, value)
    
    session.add(db_queue)
    await session.commit()
    await session.refresh(db_queue)
    
    # Update extensionslist
    if 'extensionslist' in queue_data:
        existing_links = {link.id for link in db_queue.extensionslist}
        new_links = {ext['id'] if isinstance(ext, dict) else ext for ext in queue_data['extensionslist']}
        
        # Add new links
        for ext_id in new_links - existing_links:
            link = Extensiontoqueuelink(queue_id=queue_id, extension_id=ext_id)
            session.add(link)
        
        await session.commit()
        await session.refresh(db_queue)
    
    return db_queue

# Add endpoints to manage the links between queues and extensions
@router.post("/queues/{queue_id}/extension/{extension_id}", response_model=Queue, tags=["queues"])
async def add_extension_to_queue(
    queue_id: int,
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    queue_result = await session.execute(select(Queues).filter(Queues.id == queue_id))
    db_queue = queue_result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")

    extension_result = await session.execute(select(Extensions).filter(Extensions.id == extension_id))
    db_extension = extension_result.scalar_one_or_none()
    if db_extension is None:
        raise HTTPException(status_code=404, detail="Extension not found")

    link = Extensiontoqueuelink(queue_id=queue_id, extension_id=extension_id)
    session.add(link)
    await session.commit()
    await session.refresh(db_queue)
    return db_queue

@router.delete("/queues/{queue_id}/extension/{extension_id}", response_model=Queue, tags=["queues"])
async def remove_extension_from_queue(
    queue_id: int,
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    link_result = await session.execute(
        select(Extensiontoqueuelink)
        .filter(Extensiontoqueuelink.queue_id == queue_id)
        .filter(Extensiontoqueuelink.extension_id == extension_id)
    )
    link = link_result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    queue_result = await session.execute(select(Queues).filter(Queues.id == queue_id))
    db_queue = queue_result.scalar_one_or_none()
    return db_queue

