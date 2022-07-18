# -*- coding: UTF-8 -*-
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import os

dbUser = os.environ.get('POSTGRES_USER')
dbPassword = os.environ.get('POSTGRES_PASSWORD')
dbServer = os.environ.get('POSTGRES_SERVER')
dbPort = os.environ.get('POSTGRES_PORT')
dbName = int(os.environ.get('POSTGRES_DB'))

dburl = 'postgres://{}:{}@{}:{}/{}'.format(dbUser, dbPassword, dbServer, dbPort, dbName)
#os.environ.get('DATABASE_URL')


# create an engine
engine = create_engine(dburl)
DBSession = sessionmaker(bind=engine)
DbSession = DBSession()


@as_declarative()
class Base:
    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


Base.metadata.bind = engine
