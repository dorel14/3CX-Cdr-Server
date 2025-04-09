#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import socket
import time

def check_tcp_server():
    """Vérifie si le serveur TCP est en écoute sur le port configuré"""
    try:
        port = int(os.environ.get('SERVER_PORT', 5000))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Timeout de 5 secondes
        s.connect(('localhost', port))
        # Envoyer un message de healthcheck
        s.sendall(b'HEALTHCHECK\r\n')
        # Attendre une réponse
        response = s.recv(1024)
        s.close()
        # Vérifier si la réponse est "OK"
        return response.strip() == b'OK'
    except (socket.error, ValueError) as e:
        print(f"Erreur lors de la vérification du serveur TCP: {str(e)}")
        return False

def check_file_transfer_service():
    """
    Vérifie si le service de transfert de fichiers est en cours d'exécution
    en vérifiant l'accès aux répertoires et la création d'un fichier de test
    """
    try:
        filefolder = '/home/appuser/cdrfiles/'
        # Vérifier si le répertoire existe et est accessible
        if not os.path.isdir(filefolder):
            print(f"Le répertoire {filefolder} n'existe pas ou n'est pas accessible")
            return False
            
        # Créer un fichier temporaire pour vérifier les permissions d'écriture
        test_file = os.path.join(filefolder, f'healthcheck_{int(time.time())}.tmp')
        with open(test_file, 'w') as f:
            f.write('healthcheck')
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"Erreur lors de la vérification du service de transfert de fichiers: {str(e)}")
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