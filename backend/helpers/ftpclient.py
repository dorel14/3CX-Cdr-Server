# -*- coding: UTF-8 -*-
import os
from datetime import datetime
import ftputil
import traceback
import shutil
from time import sleep
from pathlib import Path
from .logging import logger
from .traitement_fichier import csv_files_read

path = Path(__file__).resolve()
dir_path = path.parent
working_path = path.cwd()

savefolder = datetime.today().strftime('%d%m%Y')


class FTPClient:
    """
    Provides a context manager for interacting with an FTP server.
    
    The `FTPClient` class provides a convenient way to connect to an FTP server, download new files, move files to an archive folder, and periodically check for new files.
    
    The class uses the `ftputil` library to handle the FTP connection and file operations.
    
    Example usage:
    
    with FTPClient('ftp.example.com', 'username', 'password', '/remote/directory', 60) as ftp_client:
        ftp_client.monitor('/remote/directory', '/local/directory', '/archive/directory', 60)
    
    """
        
    def __init__(self, host, user, password, server_dir, interval):
        self.host = host
        self.user = user
        self.password = password
        self.server_dir = server_dir
        self.interval = interval
        self.ftp = None

    def __enter__(self):
        self.ftp = ftputil.FTPHost(self.host, self.user, self.password)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.ftp:
            self.ftp.close()
            if exc_type is not None:
                # Gérer l'exception ici
                logger.debug(f"Une exception de type {exc_type} s'est produite : {exc_value}")
                # Vous pouvez également utiliser traceback pour obtenir plus d'informations sur l'exception
                logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))

    def download_new_files(self, ftp_folder, local_folder):
        """
        Download new files from an FTP server and return a list of the local file paths.
        
        This method connects to the FTP server, changes to the specified FTP folder, and checks each file in the folder. If the local file does not exist or the remote file is newer than the local file, the method downloads the remote file to the local folder and adds the local file path to the `new_files` list.
        
        Args:
            ftp_folder (str): The remote FTP folder to check for new files.
            local_folder (str): The local folder to download new files to.
        
        Returns:
            list: A list of the local file paths for the new files that were downloaded.
        """
                
        new_files = []
        with ftputil.FTPHost(self.host, self.user, self.password) as ftp:
            ftp.chdir(ftp_folder)
            for remote_file in ftp.listdir(ftp.getcwd()):
                local_file = os.path.join(local_folder, remote_file)
                logger.info(remote_file)
                if not remote_file.endswith('.old'):
                    ftp.download_if_newer(remote_file, local_file)
                    logger.info("file downloaded:" + remote_file)
                    if os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'ARCHIVE':
                        ftp.rename(remote_file, remote_file + ".old")
                    elif os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'DELETE':
                        ftp.remove(remote_file)
                    new_files.append(local_file)
        return new_files

    def move_files(self, files, archive_folder):
        """
        Move the specified files to the archive folder.
        
        Args:
            files (list): A list of file paths to move.
            archive_folder (str): The path to the archive folder where the files will be moved.
        
        This function takes a list of file paths and moves each file to the specified archive folder. The basename (filename) of each file is preserved in the archive folder.
        """
                
        for file in files:
            shutil.move(file, os.path.join(archive_folder, os.path.basename(file)))

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
            new_files = self.download_new_files(ftp_folder, local_folder)
            if new_files:
                logger.info('New files detected')
                csv_files_read(local_folder, archive_folder)
                #self.move_files(new_files, archive_folder)
            sleep(interval)

    def monitor(self, ftp_folder, local_folder, archive_folder, interval):
        """
        Continuously monitors an FTP folder, downloads any new files to a local folder, processes the downloaded files, and then moves the processed files to an archive folder.
        
        This function runs in an infinite loop, checking the FTP folder at the specified interval for new files. If new files are found, they are downloaded to the local folder, processed (by calling the `csv_files_read` function), and then moved to the archive folder.
        
        Args:
            ftp_folder (str): The remote FTP folder to monitor for new files.
            local_folder (str): The local folder to download new files to.
            archive_folder (str): The folder to move processed files to.
            interval (int): The number of seconds to wait between checks for new files.
        """
                
        with self:
            self.run(ftp_folder, local_folder, archive_folder, interval)


