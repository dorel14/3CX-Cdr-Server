from helpers.config import Config, configFile



def saveDbInfos(dbtype, **kwargs):
    Config.set(section='db',
                key='DBTYPE',
                value=dbtype)
    if dbtype ==  'sqlite':
        Config.set(section='sqlite',
                   key='SQLITE_PATH ',
                   value=kwargs.get('path'))
    else:
        port=kwargs.get('port', 5432)

        assert settings.SERVER==kwargs.get('server')
        assert settings.PORT==int(port) if isinstance(port, int)==False else 5432
        assert settings.USER==kwargs.get('user')
        assert settings.PASSWORD==kwargs.get('password')
    settings.reload()
    
