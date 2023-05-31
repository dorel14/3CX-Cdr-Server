# -*- coding: UTF-8 -*-
import glob
import os
import shutil
from datetime import datetime
from ftplib import FTP

from myhelpers.cdr import parse_cdr


path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
working_path = os.getcwd()
filefolder = os.environ.get('FTP_3CX_LOCALDIR')
savefolder = os.environ.get('FTP_3CX_SAVDIR')


def ftp_download():
    ftp = FTP(os.environ.get('FTP_3CX_HOST'))
    # Identification
    ftp.login(os.environ.get('FTP_3CX_LOGIN'),
              os.environ.get('FTP_3CX_PASSWORD'))
    ftp.cwd(os.environ.get('FTP_3CX_SRVDIR'))
    # Get All Files
    files = ftp.nlst()
    if not os.path.exists(filefolder):
        os.mkdir(filefolder)
    # Print out the files
    for file in files:
        print("Downloading..." + file)
        ftp.retrbinary("RETR " + file, open(filefolder + file, 'wb').write)
        ftp.delete(file)
    ftp.close()
    print("Download finish")


def csv_files_read():
    print(filefolder)
    for f in glob.glob(filefolder + "**"
                       + os.environ.get('FTP_3CX_FILEEXT'),
                       recursive=False):
        print(f)
        csv = open(f, 'r')
        count = 0
        while True:
            count += 1
            # Get next line from file
            line = csv.readline()
            # if line is empty
            # end of file is reached
            if not line:
                break
            testline = line.split(',')
            if testline[0].startswith('Call'):
                parse_cdr(line)
            print("Line{}: {}".format(count, line.strip()))
        csv.close()
        files_move(f)


def files_move(file):
    filename = str(os.path.basename(file))
    print(filename)
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)
    savefolderd = savefolder + year + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    savefolderd = savefolder + year + '/' + month + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    shutil.move(file, savefolderd + date + '_' + filename)  # to move files from
    print(file + ' moved')
