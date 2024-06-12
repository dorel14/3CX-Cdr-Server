# -*- coding: UTF-8 -*-
import os
import sys

# Ajoutez le répertoire parent au chemin de recherche de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#currentdir = os.path.dirname(os.path.realpath(__file__))
#parentdir = os.path.dirname(currentdir)
#sys.path.append(parentdir)


from myhelpers.logging import logger

filefolder = '/home/appuser/cdrfiles/'
archivefolder= '/home/appuser/cdrfiles/cdrfiles_archives/'

def create_client(server_type, **kwargs):
    """
    Creates a client instance based on the specified server type.
    
    Args:
        server_type (str): The type of server to connect to, either 'FTP', 'SFTP', or 'SCP'.
        **kwargs: Additional keyword arguments to pass to the specific client implementation.
    
    Returns:
        An instance of the appropriate client class (ftpclient, sftpclient, or scpclient) based on the server_type.
    
    Raises:
        ValueError: If an invalid server_type is provided.
    """
        
    if server_type == 'FTP':
        from myhelpers.ftpclient import FTPClient as ftpclient
        return ftpclient(**kwargs)
    elif server_type == 'SFTP':
        from myhelpers.sftpclient import sftpclient
        return sftpclient(**kwargs)
    elif server_type == 'SCP':
        host = kwargs.get('host')
        user = kwargs.get('user')
        password = kwargs.get('password')
        ports=kwargs.get('port', 22)
        from myhelpers.scpclient import scpclient
        return scpclient(host, user, password, ports)
    else:
        raise ValueError(f"Invalid server type: {server_type}")

def run_server(server_type, client_config):
    if server_type == 'TCP':
        logger.debug('TCP Server')
        from myhelpers.tcp_socket_server import serveur
        host = '0.0.0.0'
        port = int(os.environ.get('SERVER_PORT'))
        serveur.runserver(host, port)
    else:
        client = create_client(server_type, **client_config)
        client.monitor(client_config['server_dir'], filefolder, archivefolder, client_config['interval'])

if __name__ == '__main__':
    server_type = os.environ.get('SERVER_TYPE')
    from myhelpers.config import get_client_config
    client_config = get_client_config(server_type)

    if client_config:
        run_server(server_type, client_config)
    else:
        logger.debug(f"Invalid server type: {server_type}")