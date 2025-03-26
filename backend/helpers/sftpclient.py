# -*- coding: UTF-8 -*-
import pysftp
import os
import socket
from time import sleep
from .logging import logger
from .traitement_fichier import csv_files_read
from pathlib import Path

path = Path(__file__).resolve()
dir_path = path.parent
working_path = path.cwd()

class sftpclient:
    """
    The sftpclient class provides a convenient way to interact with an SFTP server. It allows you to:

        - Connect to an SFTP server with the provided host, user, password, and optional port, private key, and private key password.
        - Monitor an SFTP folder, download any new files to a local folder, and optionally archive or delete the files on the SFTP server.
        - Read any CSV files that were downloaded to the local folder and move them to an archive folder.

    The `monitor` method is the main entry point for interacting with the SFTP server. It will connect to the SFTP server, change to the specified `ftpfolder`, download any new files to the `localfolder`, and then either archive or delete the files on the SFTP server based on the value of the `FTP_3CX_ARCHIVE_OR_DELETE` environment variable. Finally, it will read any CSV files that were downloaded and move them to the `archivefolder`.
    """
    def __init__(self, host, user, password, server_dir, interval, port=22, private_key=None, private_key_pass=None):
        self.host = host
        self.user = user
        self.password = os.getenv("SFTP_PASSWORD", password)  # Sécurisation
        self.port = port
        self.server_dir = server_dir
        self.interval = interval
        self.private_key = private_key
        self.private_key_pass = private_key_pass

    def monitor(self, ftpfolder='', localfolder='', archivefolder='', interval=50):
        """
        Surveillance d'un dossier SFTP et gestion des fichiers.
        """

        # Vérification de la résolution du hostname
        try:
            resolved_ip = socket.gethostbyname(self.host)
            logger.info(f"Resolved {self.host} to {resolved_ip}")
        except socket.gaierror as e:
            logger.error(f"Hostname resolution failed for {self.host}: {e}")
            return

        # Sécurisation des clés hôtes
        cnopts = pysftp.CnOpts()
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts_path):
            cnopts.hostkeys.load(known_hosts_path)
        else:
            logger.warning("Le fichier known_hosts est absent. La connexion pourrait être vulnérable.")

        # Validation de l'action d'archivage/suppression
        action = os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE', 'ARCHIVE').upper()
        if action not in ['ARCHIVE', 'DELETE']:
            logger.warning(f"Valeur invalide pour 3CX_FILES_ARCHIVE_OR_DELETE : {action}. Utilisation de ARCHIVE.")
            action = 'ARCHIVE'

        try:
            with pysftp.Connection(host=self.host, port=self.port,
                                    username=self.user, password=self.password,
                                    private_key=self.private_key, private_key_pass=self.private_key_pass,
                                    cnopts=cnopts) as sftp:
                sftp.chdir(ftpfolder)
                fNames = sftp.listdir()

                for f in fNames:
                    logger.info(f"Traitement du fichier : {f}")
                    if not f.endswith('old'):
                        local_file_path = os.path.join(localfolder, f)
                        try:
                            sftp.get(f, local_file_path)
                            logger.info(f"Fichier téléchargé : {f}")

                            if action == 'ARCHIVE':
                                sftp.rename(f, f + ".old")
                            elif action == 'DELETE':
                                sftp.remove(f)
                        except Exception as e:
                            logger.error(f"Erreur lors du traitement du fichier {f} : {e}")

                csv_files_read(localfolder, archivefolder)

        except pysftp.ConnectionException as e:
            logger.error(f"Échec de la connexion SFTP : {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")

        sleep(interval)