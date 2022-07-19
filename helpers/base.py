# -*- coding: UTF-8 -*-
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import os

dbUser = 'postgres' # os.environ.get('POSTGRES_USER')
dbPassword ='postgres' # os.environ.get('POSTGRES_PASSWORD')
dbServer = 'db' #os.environ.get('POSTGRES_SERVER')
dbPort = '5432' #os.environ.get('POSTGRES_PORT')
dbName = '3cxcdr' # os.environ.get('POSTGRES_DB')

print(dbUser, dbPassword, dbServer, dbPort, dbName)
dburl = 'postgresql://' + dbUser + ':' + dbPassword + '@' + dbServer + ':' + dbPort + '/' + dbName

print(dburl)
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
