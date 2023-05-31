from fastapi import APIRouter, Depends, Query,  HTTPException
from sqlmodel import select, Session
from typing import Union, List

import os
import sys
sys.path.append(os.path.abspath('.'))

from myhelpers.base import get_session
from models.extensions import extensionsBase, extensionsRead, extensions, extensionsCreate

router = APIRouter(
    prefix='/api/v1'
)

@router.post('/extensions/', response_model=extensionsBase,tags=["extensions"])
async def create_extensions(*, 
                            session: Session = Depends(get_session),
                            extension:extensionsCreate):
    print(extension)
    db_extensions=extensions.from_orm(extension)
    session.add(db_extensions)
    session.commit()
    session.refresh(db_extensions)
    return db_extensions

@router.get('/extensions', response_model=List[extensionsRead],tags=["extensions"])
async def read_extensions(*,
                    session: Session = Depends(get_session),
                    offset:int=0,
                    limit: int = Query(default=100, lte=100),):
        db_extensions=session.exec(select(extensions).offset(offset).limit(limit)).all()
        return db_extensions

@router.get('/extension/{extension_id}', response_model=extensionsRead,tags=["extensions"])
async def read_extension(*, session: Session = Depends(get_session), extension_id:int):
        db_extension=session.get(extensions, extension_id)
        print(db_extension)
        if not db_extension:
            raise HTTPException(status_code=404, detail="Extension non trouvée")
        return db_extension
