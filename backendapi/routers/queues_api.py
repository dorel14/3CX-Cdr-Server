from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import List
from datetime import datetime


from ..helpers.base import get_session
from ..helpers.logging import logger
from ..models.queues import (
    queueBase,
    queuesRead,
    queues,
    queuesCreate,
    queueUpdate
)


router = APIRouter(prefix="/v1", tags=["queues"])

@router.post("/queues", response_model=queueBase, tags=["queues"])
async def create_queues(
    *, session: Session = Depends(get_session), queue: queuesCreate
):
    logger.info(queue)
    db_queues = queues.model_validate(queue)
    session.add(db_queues)
    session.commit()
    session.refresh(db_queues)
    return db_queues

@router.get("/queues", response_model=List[queuesRead], tags=["queues"])
async def read_queues(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    db_queues = session.exec(select(queues).offset(offset).limit(limit)).all()
    return db_queues

@router.get(
    "/queues/{queue_id}", response_model=queuesRead, tags=["queues"]
)
async def read_queue(*, session: Session = Depends(get_session), queue_id: int):
    db_queue = session.get(queues, queue_id)
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/byname/{queue}", response_model=queuesRead, tags=["queues"])
async def read_queue_by_name(
    *, session: Session = Depends(get_session), queue: str
):
    db_queue = (
        session.exec(select(queues).where(queues.queuename == queue)).first()
    )
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue

@router.get("/queues/bynumber/{queue}", response_model=queuesRead, tags=["queues"])
async def read_queue_by_number(
    *, session: Session = Depends(get_session), queue: str):
    db_queue = (
        session.exec(select(queues).where(queues.queue == queue)).first()
    )
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    return db_queue


router.delete("/queues/{queue_id}", response_model=queueBase, tags=["queues"])
async def delete_queue(*, session: Session = Depends(get_session), queue_id: int):
    db_queue = session.get(queues, queue_id)
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    session.delete(db_queue)
    session.commit()
    return db_queue

@router.patch("/queues/{queue_id}", response_model=queueBase, tags=["queues"])
async def update_queue(
    *, session: Session = Depends(get_session), queue_id: int, queue: queueUpdate
):
    db_queue = session.get(queues, queue_id)
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

