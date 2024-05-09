# -*- coding: UTF-8 -*-
import pysftp
import os
from time import sleep
from myhelpers.logging import logger
from myhelpers.traitement_fichier import csv_files_read

class sftpclient():
    def __init__(self, host, user, password, port=22, private_key=None, private_key_pass=None):
        self.host=host
        self.user=user
        self.password=password
        self.port=port
        self.private_key = private_key
        self.private_key_pass = private_key_pass
    
    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
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

        
        