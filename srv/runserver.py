# -*- coding: UTF-8 -*-
import os
import sys


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
server_type = os.environ.get('SERVER_TYPE')


if __name__ == '__main__':
    if server_type == 'TCP':
        print('TCP Server')
        from srv.tcp_socket_server import serveur
        serveur.runserver()
    elif server_type == 'FTP':
        print('FTP Client')
        from myhelpers.ftpclient import ftpclient
        from myhelpers.traitement_fichier import csv_files_read
        ftpc = ftpclient(host=os.environ.get('FTP_3CX_HOST'),
                         user=os.environ.get('FTP_3CX_LOGIN'),
                         password=os.environ.get('FTP_3CX_PASSWORD'))
        print('Ftp conected') 
        ftpc.monitor(os.environ.get('FTP_3CX_SRVDIR'),
                     int(os.environ.get('FTP_3CX_INTERVAL')))
