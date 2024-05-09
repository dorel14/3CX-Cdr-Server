# -*- coding: UTF-8 -*-
from scp import SCPClient
import paramiko
import os
from time import sleep
from myhelpers.logging import logger
from myhelpers.traitement_fichier import csv_files_read

class scpclient():
    def __init__(self, host, user, password, port=22):
        self.host=host
        self.user=user
        self.password=password
        self.port=port
    
    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, port=self.port, username= self.user, password= self.password, banner_timeout=200)
        logger.info(ftpfolder)
        sftp = ssh.open_sftp()
        sftp.chdir(ftpfolder)
            
        fNames = sftp.listdir(sftp.getcwd())
        with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
            for f in fNames:                
                logger.info(f"fichier {f}")
                if not f.endswith('.old'):
                    scpfilename = os.path.join(ftpfolder,f)
                    scp.get(remote_path=scpfilename,
                            local_path=os.path.join(localfolder, f))
                    logger.info("file downloaded:" + scpfilename)
                    if os.environ.get('SCP_3CX_ARCHIVE_OR_DELETE') == 'ARCHIVE':
                        #ssh.exec_command(f"sudo mv {scpfilename} .old")
                        sftp.rename(scpfilename,f"{scpfilename}.old")
                    elif os.environ.get('SCP_3CX_ARCHIVE_OR_DELETE') == 'DELETE':
                        ssh.exec_command(f"sudo rm -f  {scpfilename}")
            csv_files_read(localfolder, archivefolder)            
            sleep(interval)


