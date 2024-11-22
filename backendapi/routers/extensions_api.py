
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.extensions import Extensions
from ..schemas.extensions_schemas import ExtensionCreate, ExtensionUpdate, ExtensionBase


router = APIRouter(prefix="/v1", tags=["extensions"])

@router.post("/extensions", response_model=ExtensionBase, tags=["extensions"])
async def create_extensions(
    extension: ExtensionCreate,
    session: AsyncSession = Depends(get_session), 
):
    logger.info(extension)
    db_extensions = Extensions(**extension.dict())
    session.add(db_extensions)
    await session.commit()
    await session.refresh(db_extensions)
    return db_extensions


@router.get("/extensions", response_model=List[ExtensionBase], tags=["extensions"])
async def read_extensions(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_extensions = await session.execute(select(Extensions).offset(offset).limit(limit))
    return db_extensions.scalars().all()


@router.get(
    "/extensions/{extension_id}", response_model=ExtensionBase, tags=["extensions"]
)
async def read_extension(
    extension_id: int,
    session: AsyncSession = Depends(get_session),
    ):
    result = await session.execute(select(Extensions).where(Extensions.id == extension_id))
    db_extension = result.scalar_one_or_none()
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    return db_extension

@router.get(
    "/extensions/byextension/{extension}", response_model=ExtensionBase, tags=["extensions"]
)
async def read_extension_by_ext(
    extension: str,
    session: AsyncSession = Depends(get_session)
    ):
    result =   await session.exec(select(Extensions).where(Extensions.extension==extension))
    db_extensionbyextension = result.scalar_one_or_none()
    logger.info(db_extensionbyextension)
    if not db_extensionbyextension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    return db_extensionbyextension


@router.patch(
    "/extensions/{extension_id}", response_model=ExtensionBase, tags=["extensions"]
)
async def update_extension(
    extension_id: int, 
    extension:ExtensionUpdate,
    session: AsyncSession = Depends(get_session), 
):
    result = await session.execute(select(Extensions).filter(Extensions.id == extension_id))
    db_extension = result.scalar_one_or_none()
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")

    extension_data = extension.dict(exclude_unset=True)
    print(f'extensiondata: {extension_data}')    
    extension_data["date_modified"] = datetime.now()
    for key, value in extension_data.items():
        setattr(db_extension, key, value)
    session.add(db_extension)
    await session.commit()
    await session.refresh(db_extension)
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
