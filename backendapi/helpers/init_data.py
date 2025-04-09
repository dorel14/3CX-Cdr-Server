# -*- coding: UTF-8 -*-

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.event_types import EventsTypes
from ..helpers.logging import logger   # Import the logging module

async def create_default_event_type(session: AsyncSession):
    result = await session.execute(select(EventsTypes).filter(EventsTypes.name == "Country Holidays"))
    event_type = result.scalar_one_or_none()
    if event_type is None:
        new_event_type = EventsTypes(name="Country Holidays",
                                    description="Public holidays in the country",
                                    color="green")
        session.add(new_event_type)
        await session.commit()
        await session.refresh(new_event_type)
        logger.debug("Country Holidays Type created")
