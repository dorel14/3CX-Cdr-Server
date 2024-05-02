# -*- coding: UTF-8 -*-
import glob
import os
import shutil
from datetime import datetime
from ftplib import FTP
import ftputil
from time import sleep
from myhelpers.logging import logger
from myhelpers.traitement_fichier import csv_files_read

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
working_path = os.getcwd()

savefolder = datetime.today().strftime('%d%m%Y')

class ftpclient():
    def __init__(self, host, user, password):
        self.host=host
        self.user=user
        self.password=password
    
    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
        with ftputil.FTPHost(self.host, self.user, self.password) as ftp:
            ftp.set_time_shift(round((datetime.now() - datetime.utcnow()).seconds, -2))
            ftp.chdir(ftpfolder)
            fNames = ftp.listdir(ftp.getcwd())
            for f in fNames:
                logger.info(f)
                if not f.endswith('old'):
                    ftp.download_if_newer(f,
                                          os.path.join(localfolder, f))
                    logger.info("file downloaded:" + f)
                    ftp.rename(f, f + ".old")
            csv_files_read(localfolder, archivefolder)            
            sleep(interval)



