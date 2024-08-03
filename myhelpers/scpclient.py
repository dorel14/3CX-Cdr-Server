# -*- coding: UTF-8 -*-
from scp import SCPClient
import paramiko
import os
import fnmatch
from time import sleep
from myhelpers.logging import logger
from myhelpers.traitement_fichier import csv_files_read

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
    
    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
        """
        Monitors an SCP folder, downloads any new files matching a specified file extension, and optionally archives or deletes the downloaded files on the FTP server.
        
        Args:
            ftpfolder (str): The path to the FTP folder to monitor.
            localfolder (str): The local folder to download files to.
            archivefolder (str): The local folder to archive downloaded files to.
            interval (int): The number of seconds to wait between checks for new files.
        
        Returns:
            None
        """
                
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, port=self.port, username= self.user, password= self.password, banner_timeout=200)
        #logger.info(ftpfolder)
        sftp = ssh.open_sftp()
        sftp.chdir(ftpfolder)
            
        fNames = sftp.listdir(sftp.getcwd())
        with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
            for f in fNames:                
                logger.info(f"fichier {f}")
                scpfilename = os.path.join(ftpfolder,f)
                if fnmatch.fnmatch(f, os.environ.get('3CX_FILEEXT')) :
                    try:
                        sftp.stat(scpfilename)
                    except IOError as e:
                        logger.warning(f"Impossible de téléchareger {scpfilename} : {e}")
                        continue
                                       
                    scp.get(remote_path=scpfilename,
                            local_path=os.path.join(localfolder, f))
                    logger.info("file downloaded:" + scpfilename)
                    if os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'ARCHIVE':
                        #ssh.exec_command(f"sudo mv {scpfilename} .old")
                        sftp.rename(scpfilename,f"{scpfilename}.old")
                    elif os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'DELETE':
                        ssh.exec_command(f"sudo rm -f  {scpfilename}")
            csv_files_read(localfolder, archivefolder)            
            sleep(interval)


