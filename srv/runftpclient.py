# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from myhelpers.ftpclient import ftpclient
from myhelpers.traitement_fichier import csv_files_read
from myhelpers.logging import logger


def runftp():
    ftpc = ftpclient(host=os.environ.get('FTP_3CX_HOST'),
                 user=os.environ.get('FTP_3CX_LOGIN'),
                 password=os.environ.get('FTP_3CX_PASSWORD'))
    logger.info('Ftp conected')
    newfiles = ftpc.monitor(ftpfolder=os.environ.get('FTP_3CX_SRVDIR'), interval=int(os.environ.get('FTP_3CX_INTERVAL')))
    if newfiles :
        logger.info('New files detected')
        ftpc.ftp_download(ftpfolder=os.environ.get('FTP_3CX_SRVDIR'),
                          localfolder=os.environ.get('LOCAL_CDR_FOLDER_ARCHIVE'),
                          filestodownload=newfiles,
                          deletefiles=False)
        logger.info('New files downloaded')
        csv_files_read(os.environ.get('LOCAL_CDR_FOLDER_ARCHIVE'))
        




