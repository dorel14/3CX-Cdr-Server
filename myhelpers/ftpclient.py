# -*- coding: UTF-8 -*-
import glob
import os
import shutil
from datetime import datetime
from ftplib import FTP
from time import sleep
from myhelpers.logging import logger

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
working_path = os.getcwd()
filefolder = '/opt/cdrfiles'
savefolder = datetime.today().strftime('%d%m%Y')

class ftpclient():
    def __init__(self, host, user, password):
        self.host=host
        self.user=user
        self.password=password
    
    def monitor(self, ftpfolder='', interval=50):
        with FTP(self.host) as ftp:
            ftp.set_debuglevel(0)
            logger.info("monitor On")
            ftp.login(self.user, self.password)
            ftp.cwd(ftpfolder)
            # initialize the latest file info
            latestFileTime = None
            latestFilename = None
            for fname in ftp.nlst():
                print(fname)
                try:
                    fTimeInfo = ftp.voidcmd(f"MDTM {fname}")
                    fTime = fTimeInfo.split(" ")[1]
                    if latestFileTime!=None:
                        if fTime >= latestFileTime:
                            latestFileTime = fTime
                            latestFilename = fname
                        else:
                            latestFileTime = fTime
                            latestFilename = fname
                    print(f"latest is: {latestFilename}")
                except:
                    print(f"error while processing {fname}")
            sleep(interval)






     
    

    def ftp_download(self, ftpfolder, localfolder,filestodownload ,deletefiles:False):
        with FTP(self.host) as ftp:
            ftp.set_debuglevel(0)
            # Identification
            ftp.login(self.user, self.password)
            logger.info("FTP download Logged in")
            print("filetodownoad:" , type(filestodownload) , filestodownload)
            ftp.cwd(ftpfolder)
            if not os.path.exists(localfolder):
                os.mkdir(localfolder)
            # Print out the files
            for file in filestodownload:
                logger.info("Downloading...: " + file)
                with open(os.path.join(localfolder,file), 'wb') as f :
                    ftp.retrbinary('RETR' +file, f.write)
                if deletefiles is True:
                    ftp.delete(file)
                    logger.info("Files deleted")
            ftp.quit()
            logger.info("Download finish")



