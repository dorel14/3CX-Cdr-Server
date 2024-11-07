# -*- coding: UTF-8 -*-
import os

def get_client_config(server_type):
    env_vars = {
        'FTP_3CX_HOST': os.environ.get('FTP_3CX_HOST'),
        'FTP_3CX_LOGIN': os.environ.get('FTP_3CX_LOGIN'),
        'FTP_3CX_PASSWORD': os.environ.get('FTP_3CX_PASSWORD'),
        'FTP_3CX_SRVDIR': os.environ.get('FTP_3CX_SRVDIR'),
        '3CX_FILES_INTERVAL': int(os.environ.get('3CX_FILES_INTERVAL', '60')),
        'FTP_3CX_PORT': int(os.environ.get('FTP_3CX_PORT', '22')),
        'FTP_3CX_PRIVATE_KEY_PATH': os.environ.get('FTP_3CX_PRIVATE_KEY_PATH'),
        'FTP_3CX_PRIVATE_KEY_PASSWORD': os.environ.get('FTP_3CX_PRIVATE_KEY_PASSWORD'),
        'SCP_3CX_HOST': os.environ.get('SCP_3CX_HOST'),
        'SCP_3CX_LOGIN': os.environ.get('SCP_3CX_LOGIN'),
        'SCP_3CX_PASSWORD': os.environ.get('SCP_3CX_PASSWORD'),
        'SCP_3CX_PORT': int(os.environ.get('SCP_3CX_PORT', '22')),
        'SCP_3CX_SRVDIR': os.environ.get('SCP_3CX_SRVDIR'),
        'SERVER_PORT': int(os.environ.get('SERVER_PORT', 5000')),
    }

    if server_type == 'FTP':
        return {
            'host': env_vars['FTP_3CX_HOST'],
            'user': env_vars['FTP_3CX_LOGIN'],
            'password': env_vars['FTP_3CX_PASSWORD'],
            'server_dir': env_vars['FTP_3CX_SRVDIR'],
            'interval': env_vars['3CX_FILES_INTERVAL'],
        }
    elif server_type == 'SFTP':
        return {
            'host': env_vars['FTP_3CX_HOST'],
            'user': env_vars['FTP_3CX_LOGIN'],
            'password': env_vars['FTP_3CX_PASSWORD'],
            'port': env_vars['FTP_3CX_PORT'],
            'private_key': env_vars['FTP_3CX_PRIVATE_KEY_PATH'],
            'private_key_pass': env_vars['FTP_3CX_PRIVATE_KEY_PASSWORD'],
            'server_dir': env_vars['FTP_3CX_SRVDIR'],
            'interval': env_vars['3CX_FILES_INTERVAL'],
        }
    elif server_type == 'SCP':
        return {
            'host': env_vars['SCP_3CX_HOST'],
            'user': env_vars['SCP_3CX_LOGIN'],
            'password': env_vars['SCP_3CX_PASSWORD'],
            'port': env_vars['SCP_3CX_PORT'],
            'server_dir': env_vars['SCP_3CX_SRVDIR'],
            'interval': env_vars['3CX_FILES_INTERVAL'],
        }
    elif server_type == 'TCP':
        return {
            'host': '0.0.0.0',
            'port': env_vars['SERVER_PORT']
        }
    else:
        return None