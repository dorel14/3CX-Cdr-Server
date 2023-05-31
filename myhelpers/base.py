# -*- coding: UTF-8 -*-
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

load_dotenv()
dbUser = os.environ.get('POSTGRES_USER')
dbPassword = os.environ.get('POSTGRES_PASSWORD')
dbServer = os.environ.get('POSTGRES_SERVER')
dbPort = os.environ.get('POSTGRES_PORT')
dbName = os.environ.get('POSTGRES_DB')


dburl = f'postgresql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}'#os.environ.get('DATABASE_URL')
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

print(dburl)
# create an engine
engine = create_engine(dburl, echo=True, future=True)
metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION

async def get_session():
    session = sessionmaker(
        engine, class_=Session, expire_on_commit=False
    )
    with session() as session:
        yield session


