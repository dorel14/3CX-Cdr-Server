# -*- coding: UTF-8 -*-
import pysftp
import os
from time import sleep
from myhelpers.logging import logger
from myhelpers.traitement_fichier import csv_files_read

from pathlib import Path
path = Path(__file__).resolve()
dir_path = path.parent
working_path = path.cwd()
class sftpclient():
    """
    The `sftpclient` class provides a convenient way to interact with an SFTP server. It allows you to:
    
    - Connect to an SFTP server with the provided host, user, password, and optional port, private key, and private key password.
    - Monitor an SFTP folder, download any new files to a local folder, and optionally archive or delete the files on the SFTP server.
    - Read any CSV files that were downloaded to the local folder and move them to an archive folder.
    
    The `monitor` method is the main entry point for interacting with the SFTP server. It will connect to the SFTP server, change to the specified `ftpfolder`, download any new files to the `localfolder`, and then either archive or delete the files on the SFTP server based on the value of the `FTP_3CX_ARCHIVE_OR_DELETE` environment variable. Finally, it will read any CSV files that were downloaded and move them to the `archivefolder`.
    """
        
    def __init__(self, host, user, password, port=22, private_key=None, private_key_pass=None):
        self.host=host
        self.user=user
        self.password=password
        self.port=port
        self.private_key = private_key
        self.private_key_pass = private_key_pass
    
    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
        """
        Monitors an SFTP folder, downloads any new files to a local folder, and optionally archives or deletes the files on the SFTP server. It then reads any CSV files that were downloaded and moves them to an archive folder.
        
        Args:
            ftpfolder (str): The SFTP folder to monitor.
            localfolder (str): The local folder to download files to.
            archivefolder (str): The folder to move CSV files to.
            interval (int): The number of seconds to wait between checks.
        
        Returns:
            None
        """
                
        with pysftp.Connection(hostname=self.host, port=self.port,
                               username=self.user, password=self.password, 
                               private_key=None, private_key_pass=None) as sftp :
            sftp.chdir(ftpfolder)
            fNames = sftp.listdir(sftp.getcwd())
            for f in fNames:
                logger.info(f)
                if not f.endswith('old'):
                    sftp.get(f, os.path.join(localfolder, f))
                    logger.info("file downloaded:" + f)
                    if os.environ.get('FTP_3CX_ARCHIVE_OR_DELETE') == 'ARCHIVE':
                        sftp.rename(f, f + ".old")
                    elif os.environ.get('FTP_3CX_ARCHIVE_OR_DELETE') == 'DELETE':
                        sftp.remove(f)
            csv_files_read(localfolder, archivefolder)            
            sleep(interval)

        
        