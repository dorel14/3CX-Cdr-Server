# -*- coding: UTF-8 -*-
import os
import sys


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
server_type = os.environ.get('SERVER_TYPE')
filefolder = '/home/appuser/cdrfiles/'
archivefolder= '/home/appuser/cdrfiles/cdrfiles_archives/'

if __name__ == '__main__':
    if server_type == 'TCP':
        print('TCP Server')
        from srv.tcp_socket_server import serveur
        serveur.runserver()
    elif server_type == 'FTP':
        print('FTP Client')
        from myhelpers.ftpclient import ftpclient
        ftpc = ftpclient(host=os.environ.get('FTP_3CX_HOST'),
                         user=os.environ.get('FTP_3CX_LOGIN'),
                         password=os.environ.get('FTP_3CX_PASSWORD'))
        print('Ftp conected') 
        ftpc.monitor(os.environ.get('FTP_3CX_SRVDIR'),
                     filefolder,
                     archivefolder,
                     int(os.environ.get('FTP_3CX_INTERVAL')))
    elif server_type=='SFTP':
        print('SFTP client')
        from myhelpers.sftpclient import sftpclient
        sftpc = sftpclient(host=os.environ.get('FTP_3CX_HOST'),
                         user=os.environ.get('FTP_3CX_LOGIN'),
                         password=os.environ.get('FTP_3CX_PASSWORD'),
                         port=os.environ.get('FTP_3CX_PORT'),
                         private_key=os.environ.get('FTP_3CX_PRIVATE_KEY_PATH'),
                         private_key_pass=os.environ.get('FTP_3CX_PRIVATE_KEY_PASSWORD'))
        print('Ftp conected') 
        sftpc.monitor(os.environ.get('FTP_3CX_SRVDIR'),
                     filefolder,
                     archivefolder,
                     int(os.environ.get('FTP_3CX_INTERVAL')))
    elif server_type=='SCP':
        print('SCP client')
        from myhelpers.scpclient import scpclient
        scpc = scpclient(host=os.environ.get('SCP_3CX_HOST'),
                         user=os.environ.get('SCP_3CX_LOGIN'),
                         password=os.environ.get('SCP_3CX_PASSWORD'),
                         port=os.environ.get('SCP_3CX_PORT'))
        print('scp conected') 
        scpc.monitor(os.environ.get('SCP_3CX_SRVDIR'),
                     filefolder,
                     archivefolder,
                     int(os.environ.get('SCP_3CX_INTERVAL')))
