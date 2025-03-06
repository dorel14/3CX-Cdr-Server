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
from ..socket_instance import broadcast_message

router = APIRouter(prefix="/v1", tags=["queues"])



@router.post("/queues", response_model=Queue, tags=["queues"])
async def create_queues(
    queue: QueueCreate,
    session: AsyncSession = Depends(get_session)    
):
    async with session as s:
        logger.info(queue)
        queue_data = queue.dict(exclude={"extensionslist"})
        db_queues = Queues(**queue_data)
        s.add(db_queues)
        await s.flush()  # Pour obtenir l'ID de la queue
        
        # Add extensions links
        if queue.extensionslist:
            for ext in queue.extensionslist:
                link = Extensiontoqueuelink(queue_id=db_queues.id, extension_id=ext.id)
                s.add(link)
        await s.commit()

        # Reload the queue with its relationships
        result = await s.execute(
            select(Queues)
            .options(selectinload(Queues.extensionslist))
            .filter(Queues.id == db_queues.id)
        )

        db_queues = result.scalar_one()
        
        # Create WebSocket message after commit and refresh
        queue_dict = {
            'id': db_queues.id,
            'queue': db_queues.queue,
            'queuename': db_queues.queuename,
            'extensionslist': [{
                'id': ext.id,
                'extension': ext.extension,
                'name': ext.name
            } for ext in db_queues.extensionslist]
        }

        await broadcast_message({'action': 'create', 'queue': queue_dict})
        return db_queues

@router.get("/queues", response_model=List[Queue], tags=["queues"])
async def read_queues(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    async with session as s:
        db_queues = await s.execute(select(Queues)
                                    .options(selectinload(Queues.extensionslist))
                                    .offset(offset)
                                    .limit(limit))
        return db_queues.scalars().all()

@router.get("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def read_queue(
    queue_id: int,
    session: AsyncSession = Depends(get_session)
    ):
    async with session as s:
        result = await s.execute(
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
    async with session as s:
        result = await s.execute(select(Queues)
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

    async with session as s:
        result  = await s.execute(select(Queues)
                                    .options(selectinload(Queues.extensionslist))
                                    .where(Queues.queue == queue))
        db_queue = result.scalar_one_or_none()
        if db_queue is None:
            raise HTTPException(status_code=404, detail="Queue not found")
        return db_queue

@router.delete("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def delete_queue(*, session: AsyncSession = Depends(get_session), queue_id: int):
    async with session as s:
        resultqueue = await s.execute(select(Queues).filter(Queues.id == queue_id))
        db_queue = resultqueue.scalar_one_or_none()
        if db_queue is None:
            raise HTTPException(status_code=404, detail="Queue not found")
        queue_dict = {
            'id': db_queue.id,
            'queue': db_queue.queue,
            'queuename': db_queue.queuename
        }
        await s.delete(db_queue)
        await s.commit()
        message = {'action': 'delete', 'queue': queue_dict}
        print(f"Broadcasting delete message: {message}")  # Debug log
        await broadcast_message(message)        
        return db_queue

@router.patch("/queues/{queue_id}", response_model=Queue, tags=["queues"])
async def update_queue(
    queue_id: int,
    queue: QueueUpdate,
    session: AsyncSession = Depends(get_session),
    ):
    async with session as s:
        result  =  await s.execute(select(Queues)
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
        
        s.add(db_queue)
        await s.commit()
        
        # Update extensionslist
        if 'extensionslist' in queue_data:
            existing_links = {link.extension for link in db_queue.extensionslist}
            new_links = {ext['id'] if isinstance(ext, dict) else ext for ext in queue_data['extensionslist']}
            
            # Add new links
            for ext_id in new_links - existing_links:
                link = Extensiontoqueuelink(queue_id=queue_id, extension_id=ext_id)
                s.add(link)
            
            await s.commit()
        # Reload the queue with its relationships
        result = await s.execute(
            select(Queues)
            .options(selectinload(Queues.extensionslist))
            .filter(Queues.id == db_queue.id)
        )

        db_queues = result.scalar_one()
        
        # Create WebSocket message after commit and refresh
        queue_dict = {
            'id': db_queues.id,
            'queue': db_queues.queue,
            'queuename': db_queues.queuename,
            'extensionslist': [{
                'id': ext.id,
                'extension': ext.extension,
                'name': ext.name
            } for ext in db_queues.extensionslist]
        }

        await broadcast_message({'action': 'update', 'queue': queue_dict})
        return db_queue

# Add endpoints to manage the links between queues and extensions
@router.post("/queues/{queue_id}/extension/{extension_id}", response_model=Queue, tags=["queues"])
async def add_extension_to_queue(
    queue_id: int,
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        queue_result = await s.execute(select(Queues).filter(Queues.id == queue_id))
        db_queue = queue_result.scalar_one_or_none()
        if db_queue is None:
            raise HTTPException(status_code=404, detail="Queue not found")

        extension_result = await s.execute(select(Extensions).filter(Extensions.id == extension_id))
        db_extension = extension_result.scalar_one_or_none()
        if db_extension is None:
            raise HTTPException(status_code=404, detail="Extension not found")

        link = Extensiontoqueuelink(queue_id=queue_id, extension_id=extension_id)
        s.add(link)
        await s.commit()
        await s.refresh(db_queue)
        return db_queue

@router.delete("/queues/{queue_id}/extension/{extension_id}", response_model=Queue, tags=["queues"])
async def remove_extension_from_queue(
    queue_id: int,
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        link_result = await s.execute(
            select(Extensiontoqueuelink)
            .filter(Extensiontoqueuelink.queue_id == queue_id)
            .filter(Extensiontoqueuelink.extension_id == extension_id)
        )
        link = link_result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=404, detail="Link not found")

        await s.delete(link)
        await s.commit()

        queue_result = await s.execute(select(Queues).filter(Queues.id == queue_id))
        db_queue = queue_result.scalar_one_or_none()
        return db_queue

@router.delete("/queues/{queue_id}/extensions", tags=["queues"])
async def delete_queue_extension_links(
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        # Delete all extension links for this queue
        await s.execute(
            delete(Extensiontoqueuelink).where(Extensiontoqueuelink.queue_id == queue_id)
        )
        await s.commit()
        return {"message": "All extension links deleted successfully"}