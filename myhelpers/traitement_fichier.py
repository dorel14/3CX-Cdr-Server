# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil
from myhelpers.cdr import parse_cdr

filefolder = '/opt/cdrfiles'
savefolder = '/opt/cdrfiles_archives'

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
                cdrs, cdrdetails = parse_cdr(line)
                print('cdr: ', cdrs)
                print('cdrdetails: ', cdrdetails)
            print("Line{}: {}".format(count, line.strip()))
        csv.close()


def files_move(file):
    filename = str(os.path.basename(file))
    print(filename)
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)
    savefolderd = savefolder + '/' + year + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    savefolderd = savefolder + '/'+ year + '/' + month + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    shutil.move(file, savefolderd + date + '_' + filename)  # to move files from
    print(file + ' moved')