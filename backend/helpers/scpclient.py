# -*- coding: utf-8 -*-
import os
import paramiko
import traceback
import socket
from time import sleep
from .logging import logger
from .traitement_fichier import csv_files_read

class scpclient():
    """
    Provides a class `scpclient` that handles connecting to an FTP server, downloading files that are newer than the local versions, and optionally archiving or deleting the downloaded files on the FTP server.
    """
    def __init__(self, host, user, password, port=22):
        """
        Initializes an instance of the `scpclient` class with the specified FTP server host, username, and password.
        """
        self.host=host
        self.user=user
        self.password=password
        self.port=port
    def handle_remote_file(self, ssh, file_path, action="ARCHIVE", archive_folder=None):
        """
        Gère un fichier distant sur un serveur SSH/SCP (archivage ou suppression)

        Args:
            ssh (paramiko.SSHClient): Connexion SSH active
            file_path (str): Chemin du fichier à traiter
            action (str): Action à effectuer ("ARCHIVE" ou "DELETE")
            archive_folder (str, optional): Dossier d'archivage si action="ARCHIVE"

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            file_name = os.path.basename(file_path)

            if action == "ARCHIVE":
                if not archive_folder:
                    logger.error(f"Dossier d'archivage non spécifié pour {file_path}")
                    return False

                # Exécuter des commandes via SSH pour gérer les fichiers
                # Vérifier si le dossier d'archive existe, sinon le créer
                stdin, stdout, stderr = ssh.exec_command(f"test -d {archive_folder} || mkdir -p {archive_folder}")
                if stderr.read():
                    logger.error(f"Erreur lors de la vérification/création du dossier {archive_folder}")
                    return False

                # Archiver le fichier (renommer/déplacer)
                archive_path = os.path.join(archive_folder, file_name)
                logger.info(f"Archivage du fichier {file_path} vers {archive_path}")
                stdin, stdout, stderr = ssh.exec_command(f"mv {file_path} {archive_path}")
                error = stderr.read()
                if error:
                    logger.error(f"Erreur lors de l'archivage du fichier {file_path}")
                    return False
                logger.info(f"Fichier {file_name} archivé avec succès")

            elif action == "DELETE":
                logger.info(f"Suppression du fichier {file_path}")
                stdin, stdout, stderr = ssh.exec_command(f"rm {file_path}")
                error = stderr.read()
                if error:
                    logger.error(f"Erreur lors de la suppression du fichier {file_path}")
                    return False
                logger.info(f"Fichier {file_name} supprimé avec succès")

            else:
                logger.warning(f"Action non reconnue: {action}. Fichier {file_path} non traité.")
                return False

            return True

        except paramiko.SSHException as e:
            logger.error(f"Erreur SSH lors du traitement de {file_path}: {str(e)}")
        except paramiko.AuthenticationException as e:
            logger.error(f"Erreur d'authentification lors du traitement de {file_path}: {str(e)}")
        except paramiko.ChannelException as e:
            logger.error(f"Erreur de canal SSH lors du traitement de {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement de {file_path}: {str(e)}")
            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

        return False


    def monitor(self, ftpfolder='', localfolder='', archivefolder='', interval=50):
        """
        Monitors a remote directory via SCP/SSH, downloads new files, and processes them.

        This method establishes a secure SSH connection to the remote server, downloads
        files matching the pattern specified in the 3CX_FILEEXT environment variable,
        and then either archives or deletes the remote files based on configuration.

        Args:
            ftpfolder (str): Remote directory path to monitor
            localfolder (str): Local directory to download files to
            archivefolder (str): Directory to move processed files to
            interval (int): Time in seconds between monitoring cycles

        Returns:
            None
        """
        ssh = paramiko.SSHClient()

        # Validation de l'action d'archivage/suppression
        action = os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE', 'ARCHIVE').upper()
        if action not in ['ARCHIVE', 'DELETE']:
            logger.warning(f"Valeur invalide pour 3CX_FILES_ARCHIVE_OR_DELETE : {action}. Utilisation de ARCHIVE.")
            action = 'ARCHIVE'

        while True:
            try:
                # Use system host keys
                ssh.load_system_host_keys()

                # Or load from known_hosts file
                known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
                if os.path.exists(known_hosts_path):
                    ssh.load_host_keys(known_hosts_path)

                # Reject unknown hosts by using the default policy
                ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

                # Connect with strict host key checking
                logger.info(f"Connecting to {self.host}:{self.port} as {self.user}")
                ssh.connect(
                    hostname=self.host, 
                    port=self.port, 
                    username=self.user, 
                    password=self.password
                )

                # Déterminer l'extension de fichier à surveiller
                file_extension = os.environ.get('3CX_FILEEXT', '.csv')

                # Lister les fichiers dans le dossier distant
                stdin, stdout, stderr = ssh.exec_command(f"find {ftpfolder} -type f -name '*{file_extension}'")
                files = stdout.read().decode().strip().split('\n')

                downloaded_files = False

                for file_path in files:
                    if not file_path:  # Ignorer les lignes vides
                        continue

                    file_name = os.path.basename(file_path)
                    local_file_path = os.path.join(localfolder, file_name)

                    # Télécharger le fichier
                    try:
                        # Créer un client SCP à partir de la session SSH
                        scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
                        scp.get(file_path, local_file_path)
                        logger.info(f"Fichier téléchargé: {file_name}")
                        downloaded_files = True

                        # Gérer le fichier distant (archiver ou supprimer)
                        archive_folder = os.path.join(ftpfolder, 'cdrfiles_archives') if action == 'ARCHIVE' else None
                        self.handle_remote_file(ssh, file_path, action, archive_folder)

                    except Exception as e:
                        logger.error(f"Erreur lors du téléchargement du fichier {file_name}: {str(e)}")
                        logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

                # Traiter les fichiers téléchargés avec la fonction existante
                if downloaded_files:
                    logger.info('New files detected')
                    csv_files_read(localfolder, archivefolder)

                # Fermer la connexion SSH
                ssh.close()

                # Attendre avant la prochaine vérification
                logger.info(f"Attente de {interval} secondes avant la prochaine vérification")
                sleep(interval)

            except paramiko.SSHException as e:
                logger.error(f"Erreur SSH: {str(e)}")
            except socket.error as e:
                logger.error(f"Erreur de socket: {str(e)}")
            except Exception as e:
                logger.error(f"Erreur inattendue: {str(e)}")
                logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

            # En cas d'erreur, attendre avant de réessayer
            logger.info(f"Tentative de reconnexion dans {interval} secondes")
            sleep(interval)

            # Fermer la connexion SSH si elle est encore ouverte
            try:
                if ssh and ssh.get_transport() and ssh.get_transport().is_active():
                    ssh.close()
            except paramiko.SSHException as e:
                logger.debug(f"Erreur lors de la fermeture de la connexion SSH: {str(e)}")
            except Exception as e:
                logger.debug(f"Erreur inattendue lors de la fermeture de la connexion SSH: {str(e)}")