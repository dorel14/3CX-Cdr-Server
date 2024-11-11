# -*- coding: UTF-8 -*-
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()
dbUser = os.environ.get('POSTGRES_USER')
dbPassword = os.environ.get('POSTGRES_PASSWORD')
dbServer = os.environ.get('POSTGRES_SERVER')
dbPort = os.environ.get('POSTGRES_PORT')
dbName = os.environ.get('POSTGRES_DB')
dburl=os.environ.get('DATABASE_URL')


#dburl = f'postgresql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}' # os.environ.get('DATABASE_URL')
#os.environ.update('DATABASE_URL',dburl)

dburl = f'postgresql+aynspg://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}' # os.environ.get('DATABASE_URL')
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

#print(dburl)
# create an engine
engine = create_async_engine(dburl, echo=True, future=True)
AsyncSessionLocal  = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
Base.metadata.naming_convention = NAMING_CONVENTION

def get_session():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
