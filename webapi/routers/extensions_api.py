from fastapi import APIRouter, Depends, Query
from sqlmodel import select,Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List
import json
from myhelpers.base import get_session

from models.extensionsandqueues import extensionsBase, extensionsCreate, extensions

router = APIRouter(
    prefix='/api/v1',
    tags=["api_v1"]
)
@router.post('/extensions/', response_model=extensionsBase,tags=["extensions"])
async def create_extensions(*, 
                            session: Session = Depends(get_session),
                            extension:extensionsCreate):
    db_extensions=extensions.from_orm(extension)
    session.add(db_extensions)
    session.commit
    session.refresh(db_extensions)
    return db_extensions

@router.get('/extensions', response_model=List[extensionsBase], tags=["extensions"])
async def read_extensions(*,
                    session: Session = Depends(get_session),
                    offset:int=0,
                    limit: int = Query(default=100, lte=100),):
    extensionlist=session.execute(select(extensions).offset(offset).limit(limit)).all()
    return extensionlist
