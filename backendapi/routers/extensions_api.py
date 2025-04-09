from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from ..helpers.base import get_session
from ..helpers.logging import logger
from ..socket_instance import broadcast_message

from ..models.extensions import Extensions
from ..models.queues import Queues
from ..models.extensionsandqueues import Extensiontoqueuelink
from ..schemas.extensions_schemas import ExtensionCreate, ExtensionUpdate, Extension

router = APIRouter(prefix="/v1", tags=["extensions"])

@router.post("/extensions", response_model=Extension, tags=["extensions"])
async def create_extensions(
    extension: ExtensionCreate,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        extension_data = extension.dict(exclude={"queues"})
        db_extension = Extensions(**extension_data)
        s.add(db_extension)
        await s.flush()

        created_id = db_extension.id

        if extension.queues:
            for queue in extension.queues:
                link = Extensiontoqueuelink(extension_id=created_id, queue_id=queue.id)
                s.add(link)
        await s.commit()

        stmt = select(Extensions).options(selectinload(Extensions.queueslist)).filter(Extensions.id == created_id)
        result = await s.execute(stmt)

        db_extension = result.unique().scalar_one()

        # Create a dictionary with the extension data
        extension_dict = {
            'id': db_extension.id,
            'extension': db_extension.extension,
            'name': db_extension.name,
            'date_added': str(db_extension.date_added),
            'date_modified': str(db_extension.date_modified)
        }
        # Broadcast the message to all connected clients
        await broadcast_message({'action': 'create', 'extension': extension_dict})
        return db_extension

@router.get("/extensions", response_model=List[Extension], tags=["extensions"])
async def read_extensions(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    async with session as s:
        db_extensions = await s.execute(select(Extensions)
                                        .options(selectinload(Extensions.queueslist)
                                                )
                                        .offset(offset)
                                        .limit(limit))
        return db_extensions.scalars().all()

@router.get(
    "/extensions/{extension_id}", response_model=Extension, tags=["extensions"]
)
async def read_extension(
    extension_id: int,
    session: AsyncSession = Depends(get_session),
    ):
    async with session as s:
        result = await s.execute(select(Extensions)
                                .options(selectinload(Extensions.queueslist)
                                        )
                                .where(Extensions.id == extension_id)
                                .order_by(Extensions.id))
        db_extension = result.scalar_one_or_none()
        if not db_extension:
            raise HTTPException(status_code=404, detail="Extension non trouvée")
        return db_extension

@router.get(
    "/extensions/byextension/{extension}", response_model=Extension, tags=["extensions"]
)
async def read_extension_by_ext(
    extension: str,
    session: AsyncSession = Depends(get_session)
    ):
    async with session as s:
        result =   await s.execute(select(Extensions)
                                    .options(selectinload(Extensions.queueslist))
                                    .where(Extensions.extension==extension))
        db_extensionbyextension = result.scalar_one_or_none()
        logger.info(db_extensionbyextension)
        if not db_extensionbyextension:
            raise HTTPException(status_code=404, detail="Extension non trouvée")
        return db_extensionbyextension

@router.patch("/extensions/{extension_id}", response_model=Extension, tags=["extensions"])
async def update_extension(
    extension_id: int, 
    extension: ExtensionUpdate,
    session: AsyncSession = Depends(get_session), 
):
    async with session as s:
        result = await s.execute(
            select(Extensions)
            .options(selectinload(Extensions.queueslist))
            .filter(Extensions.id == extension_id)
        )
        db_extension = result.unique().scalar_one()

        extension_data = extension.dict(exclude_unset=True)
        extension_data["date_modified"] = datetime.now()

        # Update basic extension attributes
        for key, value in extension_data.items():
            if key != 'queues':
                setattr(db_extension, key, value)

        # Update queue links
        if 'queues' in extension_data:
            # Get current queue IDs
            current_queue_ids = {q.id for q in db_extension.queueslist}
            # Get new queue IDs from request
            new_queue_ids = {q['id'] for q in extension_data['queues']}

            # Remove links that are no longer needed
            queues_to_remove = current_queue_ids - new_queue_ids
            if queues_to_remove:
                await s.execute(
                    delete(Extensiontoqueuelink).where(
                        Extensiontoqueuelink.extension_id == extension_id,
                        Extensiontoqueuelink.queue_id.in_(queues_to_remove)
                    )
                )

            # Add new links
            queues_to_add = new_queue_ids - current_queue_ids
            for queue_id in queues_to_add:
                link = Extensiontoqueuelink(extension_id=extension_id, queue_id=queue_id)
                s.add(link)

        await s.commit()
        await s.refresh(db_extension)

        # Create a dictionary with the extension data
        extension_dict = {
            'id': db_extension.id,
            'extension': db_extension.extension,
            'name': db_extension.name,
            'date_added': str(db_extension.date_added),
            'date_modified': str(db_extension.date_modified)
        }

        await broadcast_message({'action': 'update', 'extension': extension_dict})
        return db_extension

@router.post("/extensions/{extension_id}/queue/{queue_id}", response_model=Extension, tags=["extensions"])
async def add_queue_to_extension(
    extension_id: int,
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        extension_result = await s.execute(select(Extensions).filter(Extensions.id == extension_id))
        db_extension = extension_result.scalar_one_or_none()
        if db_extension is None:
            raise HTTPException(status_code=404, detail="Extension not found")

        queue_result = await s.execute(select(Queues).filter(Queues.id == queue_id))
        db_queue = queue_result.scalar_one_or_none()
        if db_queue is None:
            raise HTTPException(status_code=404, detail="Queue not found")

        link = Extensiontoqueuelink(extension_id=extension_id, queue_id=queue_id)
        s.add(link)
        await s.commit()
        await s.refresh(db_extension)
        return db_extension

@router.delete("/extensions/{extension_id}/queue/{queue_id}", response_model=Extension, tags=["extensions"])
async def remove_queue_from_extension(
    extension_id: int,
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    async with session as s:
        link_result = await s.execute(
            select(Extensiontoqueuelink)
            .filter(Extensiontoqueuelink.extension_id == extension_id)
            .filter(Extensiontoqueuelink.queue_id == queue_id)
        )
        link = link_result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=404, detail="Link not found")

        await s.delete(link)
        await s.commit()

        extension_result = await s.execute(select(Extensions).filter(Extensions.id == extension_id))
        db_extension = extension_result.scalar_one_or_none()
        return db_extension

@router.delete("/extensions/{extension_id}", tags=["extensions"])
async def delete_extension(
    extension_id: int,
    session: AsyncSession = Depends(get_session), 
):
    async with session as s:
        result = await s.execute(select(Extensions).filter(Extensions.id == extension_id))
        db_extension =  result.scalar_one_or_none()
        if not db_extension:
            raise HTTPException(status_code=404, detail="Extension non trouvée")
        await s.delete(db_extension)
        await s.commit()
        # Create a dictionary with the extension data
        extension_dict = {
            'id': db_extension.id,
            'extension': db_extension.extension,
            'name': db_extension.name,
            'date_added': str(db_extension.date_added),
            'date_modified': str(db_extension.date_modified)
        }

        await broadcast_message({'action': 'update', 'extension': extension_dict})
        return {"ok": True}

