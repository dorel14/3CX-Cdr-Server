# -*- coding: UTF-8 -*-

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker


from helpers.config import Config


dbName = Config.get('PG_BDD', 'db_name')
dbUser = Config.get('PG_BDD', 'db_user')
dbPassword = Config.get('PG_BDD', 'db_password')
dbServer = Config.get('PG_BDD', 'db_server')
dbPort = Config.get('PG_BDD', 'db_port')

dburl = 'postgresql://' + dbUser + ':' + dbPassword + \
    '@' + dbServer + ':' + dbPort + '/' + dbName

# create an engine
engine = create_engine(dburl)

call_data_records_meta = MetaData(engine)
call_data_records = Table('call_data_records',
                          call_data_records_meta,
                          autoload=True)
DBSession = sessionmaker(bind=engine)
DbSession = DBSession()
