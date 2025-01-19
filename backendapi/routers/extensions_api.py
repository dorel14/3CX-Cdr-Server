from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from ..helpers.base import get_session
from ..helpers.logging import logger
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
    extension_data = extension.dict(exclude={"queues"})
    db_extension = Extensions(**extension_data)
    session.add(db_extension)
    await session.flush()
    
    created_id = db_extension.id
    
    if extension.queues:
        for queue in extension.queues:
            link = Extensiontoqueuelink(extension_id=created_id, queue_id=queue.id)
            session.add(link)
    await session.commit()
    
    stmt = select(Extensions).options(selectinload(Extensions.queueslist)).filter(Extensions.id == created_id)
    result = await session.execute(stmt)
    return result.unique().scalar_one()

@router.get("/extensions", response_model=List[Extension], tags=["extensions"])
async def read_extensions(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_extensions = await session.execute(select(Extensions)
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
    result = await session.execute(select(Extensions)
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
    result =   await session.execute(select(Extensions)
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
    result = await session.execute(select(Extensions)
                                .options(selectinload(Extensions.queueslist)
                                        .selectinload(Queues.extensionslist)
                                        )
                                .filter(Extensions.id == extension_id))
    db_extension = result.scalar_one_or_none()
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")

    extension_data = extension.dict(exclude_unset=True)
    extension_data["date_modified"] = datetime.now()
    
    for key, value in extension_data.items():
        if key != 'queues':
            setattr(db_extension, key, value)

    session.add(db_extension)
    await session.commit()
    await session.refresh(db_extension)
    
    # Update queueslist
    if 'queues' in extension_data:
        existing_links = {link.id for link in db_extension.queueslist}
        new_links = {queue['id'] if isinstance(queue, dict) else queue for queue in extension_data['queues']}
        
        # Add new links
        for queue_id in new_links - existing_links:
            link = Extensiontoqueuelink(extension_id=extension_id, queue_id=queue_id)
            session.add(link)
        
        await session.commit()
        await session.refresh(db_extension)
    
    return db_extension

@router.post("/extensions/{extension_id}/queue/{queue_id}", response_model=Extension, tags=["extensions"])
async def add_queue_to_extension(
    extension_id: int,
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    extension_result = await session.execute(select(Extensions).filter(Extensions.id == extension_id))
    db_extension = extension_result.scalar_one_or_none()
    if db_extension is None:
        raise HTTPException(status_code=404, detail="Extension not found")

    queue_result = await session.execute(select(Queues).filter(Queues.id == queue_id))
    db_queue = queue_result.scalar_one_or_none()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")

    link = Extensiontoqueuelink(extension_id=extension_id, queue_id=queue_id)
    session.add(link)
    await session.commit()
    await session.refresh(db_extension)
    return db_extension

@router.delete("/extensions/{extension_id}/queue/{queue_id}", response_model=Extension, tags=["extensions"])
async def remove_queue_from_extension(
    extension_id: int,
    queue_id: int,
    session: AsyncSession = Depends(get_session)
):
    link_result = await session.execute(
        select(Extensiontoqueuelink)
        .filter(Extensiontoqueuelink.extension_id == extension_id)
        .filter(Extensiontoqueuelink.queue_id == queue_id)
    )
    link = link_result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    extension_result = await session.execute(select(Extensions).filter(Extensions.id == extension_id))
    db_extension = extension_result.scalar_one_or_none()
    return db_extension


@router.delete("/extensions/{extension_id}", tags=["extensions"])
async def delete_extension(
    extension_id: int,
    session: AsyncSession = Depends(get_session), 
):
    result = await session.execute(select(Extensions).filter(Extensions.id == extension_id))
    db_extension =  result.scalar_one_or_none()
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    await session.delete(db_extension)
    await session.commit()

    return {"ok": True}

@router.delete("/extensions/{extension_id}/queues", tags=["extensions"])
async def delete_extension_queue_links(
    extension_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Delete all queue links for this extension
    await session.execute(
        delete(Extensiontoqueuelink).where(Extensiontoqueuelink.extension_id == extension_id)
    )
    await session.commit()
    return {"message": "All queue links deleted successfully"}

