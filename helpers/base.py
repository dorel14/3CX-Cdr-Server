# -*- coding: UTF-8 -*-
from sqlalchemy.ext.automap import automap_base
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

Base = automap_base()
# create an engine
engine = create_engine(dburl)
Base.prepare(engine, reflect=True)
call_data_records = Base.classes.call_data_records
DBSession = sessionmaker(bind=engine)
DbSession = DBSession()
