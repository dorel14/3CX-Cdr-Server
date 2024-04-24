# -*- coding: UTF-8 -*-
import glob
import os
import shutil
from datetime import datetime
from ftplib import FTP
from time import sleep

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
working_path = os.getcwd()
filefolder = '/opt/cdrfiles'
savefolder = datetime.today().strftime('%d%m%Y')

class ftpclient():
    def __init__(self, host, login, password):
        self.host=host
        self.login=login
        self.password=password
    
    def monitor(self, ftpfolder='', interval=50):
        ftp = FTP(self.host)
        ftp.login(self.login, self.password)
        ftp.cwd(ftpfolder)
        old_files = []
        try:
            while True:
                new_files = ftp.nlst()
                if len(old_files) != 0 and new_files != old_files:
                    changes = [i for i in new_files if i not in old_files]
                    print(changes)
                    yield changes
                sleep(interval)
        except KeyboardInterrupt:
            ftp.quit()
    

    def ftp_download(self, ftpfolder, localfolder,filestodownload ,deletefiles:False):
        ftp = FTP(self.host)
        # Identification
        ftp.login(self.login, self.password)
        ftp.cwd(ftpfolder)
        if not os.path.exists(localfolder):
            os.mkdir(localfolder)
        # Print out the files
        for file in filestodownload:
            print("Downloading..." + file)
            ftp.retrbinary("RETR " + file, open(localfolder + file, 'wb').write)
            if deletefiles is True:
                ftp.delete(file)
        ftp.close()
        print("Download finish")



