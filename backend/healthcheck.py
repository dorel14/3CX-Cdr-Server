#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import socket
import requests
import time

def check_tcp_server():
    """Vérifie si le serveur TCP est en écoute sur le port configuré"""
    try:
        port = int(os.environ.get('SERVER_PORT', 5000))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Timeout de 5 secondes
        s.connect(('localhost', port))
        s.close()
        return True
    except (socket.error, ValueError):
        return False

def check_file_transfer_service():
    """
    Vérifie si le service de transfert de fichiers (FTP, SFTP, SCP) est en cours d'exécution
    en vérifiant la présence d'un processus Python exécutant runserver.py
    """
    try:
        # Vérifier si le processus est en cours d'exécution
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'python' and any('runserver.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                return True
        return False
    except ImportError:
        # Si psutil n'est pas disponible, vérifier simplement si le répertoire de surveillance existe
        # et s'il est accessible
        try:
            filefolder = '/home/appuser/cdrfiles/'
            os.listdir(filefolder)
            return True
        except:
            return False

if __name__ == '__main__':
    server_type = os.environ.get('SERVER_TYPE', '').upper()

    if server_type == 'TCP':
        healthy = check_tcp_server()
    elif server_type in ['FTP', 'SFTP', 'SCP']:
        healthy = check_file_transfer_service()
    else:
        print(f"Type de serveur inconnu: {server_type}")
        sys.exit(1)

    if healthy:
        print(f"Service {server_type} en bonne santé")
        sys.exit(0)
    else:
        print(f"Service {server_type} en mauvais état")
        sys.exit(1)