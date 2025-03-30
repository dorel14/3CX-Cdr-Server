# -*- coding: utf-8 -*-
import os
import ftplib
import traceback
from time import sleep
from .logging import logger
from .traitement_fichier import csv_files_read

class ftpclient():
    """
    Provides a class `ftpclient` that handles connecting to an FTP server, downloading files that are newer than the local versions, and optionally archiving or deleting the downloaded files on the FTP server.
    """
    def __init__(self, host, user, password, port=21):
        """
        Initializes an instance of the `ftpclient` class with the specified FTP server host, username, and password.
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def connect(self):
        """
        Connects to the FTP server using the host, username, and password provided during initialization.

        Returns:
            ftplib.FTP: An FTP connection object if the connection is successful, or None if the connection fails.
        """
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)
            return ftp
        except Exception as e:
            logger.error(f"Erreur de connexion FTP: {str(e)}")
            return None

    def download_new_files(self, ftp_folder, local_folder):
        """
        Downloads files from the specified FTP folder to the specified local folder if they are newer than the local versions.

        Args:
            ftp_folder (str): The remote FTP folder to download files from.
            local_folder (str): The local folder to download files to.

        Returns:
            list: A list of the names of the files that were downloaded.
        """
        downloaded_files = []
        try:
            ftp = self.connect()
            if ftp:
                ftp.cwd(ftp_folder)
                files = ftp.nlst()

                # Filtrer les fichiers selon l'extension définie dans la variable d'environnement
                file_extension = os.environ.get('3CX_FILEEXT', '.csv')
                filtered_files = [f for f in files if f.endswith(file_extension)]

                for file_name in filtered_files:
                    local_file_path = os.path.join(local_folder, file_name)

                    # Télécharger le fichier
                    with open(local_file_path, 'wb') as local_file:
                        ftp.retrbinary(f'RETR {file_name}', local_file.write)

                    downloaded_files.append(file_name)
                    logger.info(f"Fichier téléchargé: {file_name}")

                    # Gérer le fichier distant (archiver ou supprimer)
                    action = os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE', 'ARCHIVE').upper()
                    if action in ['ARCHIVE', 'DELETE']:
                        archive_folder = os.path.join(ftp_folder, 'cdrfiles_archives')
                        self.handle_remote_file(ftp, file_name, action, archive_folder if action == 'ARCHIVE' else None)

                ftp.quit()
            return downloaded_files
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement des fichiers: {str(e)}")
            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")
            return []

    def handle_remote_file(self, ftp, file_path, action="ARCHIVE", archive_folder=None):
        """
        Gère un fichier distant sur un serveur FTP (archivage ou suppression)

        Args:
            ftp (ftplib.FTP): Connexion FTP active
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
                    ftp.cwd(archive_folder)
                except ftplib.error_perm:
                    logger.info(f"Création du dossier d'archive {archive_folder}")
                    ftp.mkd(archive_folder)
                    ftp.cwd(archive_folder)

                # Archiver le fichier (renommer/déplacer)
                archive_path = os.path.join(archive_folder, file_name)
                logger.info(f"Archivage du fichier {file_path} vers {archive_path}")
                ftp.rename(file_path, archive_path)
                logger.info(f"Fichier {file_name} archivé avec succès")

            elif action == "DELETE":
                logger.info(f"Suppression du fichier {file_path}")
                ftp.delete(file_path)
                logger.info(f"Fichier {file_name} supprimé avec succès")

            else:
                logger.warning(f"Action non reconnue: {action}. Fichier {file_path} non traité.")
                return False

            return True

        except ftplib.error_perm as e:
            logger.error(f"Erreur de permission FTP lors du traitement de {file_path}: {str(e)}")
        except ftplib.error_temp as e:
            logger.error(f"Erreur temporaire FTP lors du traitement de {file_path}: {str(e)}")
        except ftplib.error_reply as e:
            logger.error(f"Erreur de réponse FTP lors du traitement de {file_path}: {str(e)}")
        except ftplib.error_proto as e:
            logger.error(f"Erreur de protocole FTP lors du traitement de {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement de {file_path}: {str(e)}")
            logger.debug(f"Détails de l'erreur: {traceback.format_exc()}")

        return False

    def run(self, ftp_folder, local_folder, archive_folder, interval):
        """
        Continuously monitors an FTP folder, downloads any new files to a local folder, processes the downloaded files, and then moves the processed files to an archive folder.

        This function runs in an infinite loop, checking the FTP folder at the specified interval for new files. If new files are found, they are downloaded to the local folder, processed (by calling the `csv_files_read` function), and then moved to the archive folder.

        Args:
            ftp_folder (str): The remote FTP folder to monitor for new files.
            local_folder (str): The local folder to download new files to.
            archive_folder (str): The folder to move processed files to.
            interval (int): The number of seconds to wait between checks for new files.
        """

        while True:
            try:
                new_files = self.download_new_files(ftp_folder, local_folder)
                if new_files:
                    logger.info('New files detected')
                    try:
                        csv_files_read(local_folder, archive_folder)
                    except Exception as e:
                        logger.error(f"Error processing CSV files: {str(e)}")
                        # Optionally, you could implement a retry mechanism or move problematic files to an "error" folder
                    #self.move_files(new_files, archive_folder)
            except Exception as e:
                logger.error(f"Error in FTP monitoring loop: {str(e)}")
            # Add a short delay before retrying to avoid tight error loops
                sleep(10)

            # Continue with the regular interval between checks
            sleep(interval)
