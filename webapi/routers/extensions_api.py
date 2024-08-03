from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import List
from datetime import datetime

import os
import sys

sys.path.append(os.path.abspath("."))


from myhelpers.base import get_session
from myhelpers.logging import logger
from models.extensions import (
    extensionsBase,
    extensionsRead,
    extensions,
    extensionsCreate,
    extensionUpdate
)

router = APIRouter(prefix="/v1", tags=["extensions"])

@router.post("/extensions", response_model=extensionsBase, tags=["extensions"])
async def create_extensions(
    *, session: Session = Depends(get_session), extension: extensionsCreate
):
    logger.info(extension)
    db_extensions = extensions.model_validate(extension)
    session.add(db_extensions)
    session.commit()
    session.refresh(db_extensions)
    return db_extensions


@router.get("/extensions", response_model=List[extensionsRead], tags=["extensions"])
async def read_extensions(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_extensions = session.exec(select(extensions).offset(offset).limit(limit)).all()
    return db_extensions


@router.get(
    "/extensions/{extension_id}", response_model=extensionsRead, tags=["extensions"]
)
async def read_extension(*, session: Session = Depends(get_session), extension_id: int):
    db_extension = session.get(extensions, extension_id)
    logger.info(db_extension)
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    return db_extension

@router.get(
    "/extensions/byextension/{extension}", response_model=extensionsRead, tags=["extensions"]
)
async def read_extension_by_ext(*, session: Session = Depends(get_session), extension: str):
    db_extensionbyextension = session.exec(select(extensions).where(extensions.extension==extension)).one_or_none()
    logger.info(db_extensionbyextension)
    if not db_extensionbyextension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    return db_extensionbyextension


@router.patch(
    "/extensions/{extension_id}", response_model=extensionsRead, tags=["extensions"]
)
async def update_extension(
    *, session: Session = Depends(get_session), extension_id: int, extension:extensionUpdate
):
    db_extension = session.get(extensions, extension_id)
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    logger.info(f'db_extensions: {db_extension}')
    logger.info(f' Extension: {extension}')
    extension_data = extension.dict(exclude_unset=True)
    print(f'extensiondata: {extension_data}')    
    extension_data["date_modified"] = datetime.now()
    for key, value in extension_data.items():
        setattr(db_extension, key, value)
    session.add(db_extension)
    session.commit()
    session.refresh(db_extension)
    return db_extension


@router.delete("/extensions/{extension_id}", tags=["extensions"])
async def delete_extension(
    *, session: Session = Depends(get_session), extension_id: int
):
    db_extension = session.get(extensions, extension_id)
    if not db_extension:
        raise HTTPException(status_code=404, detail="Extension non trouvée")
    session.delete(db_extension)
    session.commit()
    return {"ok": True}
