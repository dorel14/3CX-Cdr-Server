# -*- coding: UTF-8 -*-
from dotenv import load_dotenv
from sqlmodel import create_engine, Session as  SQLModelSession, SQLModel
import os

load_dotenv()
dbUser = os.environ.get('POSTGRES_USER')
dbPassword = os.environ.get('POSTGRES_PASSWORD')
dbServer = os.environ.get('POSTGRES_SERVER')
dbPort = os.environ.get('POSTGRES_PORT')
dbName = os.environ.get('POSTGRES_DB')



#dburl = f'postgresql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}' # os.environ.get('DATABASE_URL')
#os.environ.update('DATABASE_URL',dburl)

dburl = f'postgresql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}' # os.environ.get('DATABASE_URL')
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

#print(dburl)
# create an engine
engine = create_engine(dburl, echo=True, future=True)
metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION

def get_session():
    session = SQLModelSession(engine,
                            expire_on_commit=False,)
    try:
        yield session
    finally:
        session.close()