# -*- coding: utf-8 -*-
import os
import socket
import pysftp
import paramiko
import traceback
from time import sleep
from .logging import logger
from .traitement_fichier import csv_files_read

class sftpclient():
    """
    Provides a class `sftpclient` that handles connecting to an SFTP server, downloading files, and processing them.
    """
    def __init__(self, host, user, password=None, port=22, private_key=None, private_key_pass=None):
        """
        Initializes an instance of the `sftpclient` class with the specified SFTP server parameters.
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.private_key = private_key
        self.private_key_pass = private_key_pass

    def handle_remote_file(self, sftp, file_path, action="ARCHIVE", archive_folder=None):
        """
        Gère un fichier distant sur un serveur SFTP (archivage ou suppression)

        Args:
            sftp (paramiko.SFTPClient): Connexion SFTP active
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

                # Vérifier si le dossier d'archive existe, sinon le créer
                try:
                    sftp.stat(archive_folder)
                except FileNotFoundError:
                    logger.info("Création du dossier d'archive")
                    sftp.mkdir(archive_folder)

                # Archiver le fichier (renommer/déplacer)
                archive_path = os.path.join(archive_folder, file_name)
                logger.info(f"Archivage du fichier {file_name} vers le dossier d'archive")
                sftp.rename(file_path, archive_path)
                logger.info(f"Fichier {file_name} archivé avec succès")

            elif action == "DELETE":
                logger.info(f"Suppression du fichier {file_name}")
                sftp.remove(file_path)
                logger.info(f"Fichier {file_name} supprimé avec succès")

            else:
                logger.warning(f"Action non reconnue: {action}. Fichier {file_path} non traité.")
                return False

            return True

        except paramiko.SSHException as e:
            logger.error(f"Erreur SSH lors du traitement de {file_path}: {str(e)}")
        except paramiko.SFTPError as e:
            logger.error(f"Erreur SFTP lors du traitement de {file_path}: {str(e)}")
        except FileNotFoundError as e:
            logger.error(f"Fichier non trouvé lors du traitement de {file_path}: {str(e)}")
        except PermissionError as e:
            logger.error(f"Erreur de permission lors du traitement de {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement de {file_path}: {str(e)}")
            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

        return False

    def monitor(self, ftpfolder='', localfolder='', archivefolder='', interval=50):
        """
        Surveillance d'un dossier SFTP et gestion des fichiers.

        Args:
            ftpfolder (str): Chemin du dossier distant à surveiller
            localfolder (str): Dossier local où télécharger les fichiers
            archivefolder (str): Dossier où déplacer les fichiers traités
            interval (int): Intervalle en secondes entre les vérifications
        """

        # Vérification de la résolution du hostname
        try:
            socket.gethostbyname(self.host)
            logger.info(f"Successfully resolved hostname")
        except socket.gaierror as e:
            logger.error(f"Hostname resolution failed : {e}")
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

        while True:
            try:
                with pysftp.Connection(host=self.host,
                                        port=self.port,
                                        username=self.user,
                                        password=self.password,
                                        private_key=self.private_key,
                                        private_key_pass=self.private_key_pass,
                                        cnopts=cnopts) as sftp:
                    sftp.chdir(ftpfolder)
                    fNames = sftp.listdir()

                    # Filtrer les fichiers selon l'extension définie
                    file_extension = os.environ.get('3CX_FILEEXT', '.csv')
                    filtered_files = [f for f in fNames if f.endswith(file_extension)]

                    downloaded_files = False

                    for f in filtered_files:
                        logger.info(f"Traitement du fichier : {f}")
                        local_file_path = os.path.join(localfolder, f)
                        try:
                            sftp.get(f, local_file_path)
                            logger.info(f"Fichier téléchargé : {f}")
                            downloaded_files = True

                            # Gérer le fichier distant (archiver ou supprimer)
                            archive_folder = os.path.join(ftpfolder, 'cdrfiles_archives') if action == 'ARCHIVE' else None
                            self.handle_remote_file(sftp, f, action, archive_folder)

                        except Exception as e:
                            logger.error(f"Erreur lors du traitement du fichier {f}: {str(e)}")
                            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

                    # Traiter les fichiers téléchargés avec la fonction existante
                    if downloaded_files:
                        logger.info('New files detected')
                        csv_files_read(localfolder, archivefolder)

                # Attendre avant la prochaine vérification
                sanitized_interval = int(interval)
                if sanitized_interval < 0 or sanitized_interval > 86400:  # Ensure interval is within a reasonable range (0 to 24 hours)
                    logger.warning(f"Intervalle invalide: {sanitized_interval}. Utilisation de la valeur par défaut de 50 secondes.")
                    sanitized_interval = 50
                logger.info(f"Attente de {sanitized_interval} secondes avant la prochaine vérification")
                sleep(sanitized_interval)

            except paramiko.SSHException as e:
                logger.error(f"Erreur SSH: {str(e)}")
            except socket.error as e:
                logger.error(f"Erreur de socket: {str(e)}")
            except Exception as e:
                logger.info("Tentative de reconnexion après une erreur")
                logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")
                sleep(sanitized_interval)

            # En cas d'erreur, attendre avant de réessayer
            logger.info(f"Tentative de reconnexion dans {sanitized_interval} secondes")
            sleep(sanitized_interval)