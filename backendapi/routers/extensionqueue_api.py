# from fastapi import APIRouter, Depends
# from sqlmodel import  Session
# import os
# import sys



# from myhelpers.base import get_session
# from .models.extensionsqueue_model import Extensiontoqueuelink

# router = APIRouter(prefix="/v1")


# @router.post("/queues/{queue_id}/extension/{extension_id}/", tags=["extensions, queues"])
# def link_queue_extension(queue_id: int, extension_id: int, session: Session = Depends(get_session)):
#     link_queue_extension = Extensiontoqueuelink(queue_id=queue_id, extension_id=extension_id)
#     session.add(link_queue_extension)
#     session.commit()
#     return {"message": "Queue linked to extension successfully"}