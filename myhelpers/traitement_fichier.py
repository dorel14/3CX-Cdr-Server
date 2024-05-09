# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil

from myhelpers.cdr import parse_cdr, push_cdr_api
from myhelpers.logging import logger

#filefolder = '/opt/cdrfiles'
#savefolder = '/opt/cdrfiles_archives'

def files_move(file, savefolder):
    filename = str(os.path.basename(file))
    logger.info(filename)
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
    logger.info(file + ' moved')

def csv_files_read(filefolder, archivefolder):
    logger.info(filefolder)
    os.chdir(filefolder)
    for f in list(glob.glob(os.environ.get('3CX_FILEEXT'),
                       recursive=False)):
        logger.info(f)
        csv = open(f, 'r')
        count = 1
        while True:            
            # Get next line from file
            line = csv.readline()
            # if line is empty
            # end of file is reached
            if not line:
                break
            testline = line.split(',')
            if testline[0].startswith('Call'):
                cdrs, cdrdetails = parse_cdr(line, f)
                rcdr, rcdrdetails = push_cdr_api(cdrs, cdrdetails)
                logger.info(rcdr)
                logger.info(rcdrdetails)
            logger.info("Line{}: {}".format(count, line.strip()))
            count += 1
        csv.close()
        files_move(f, archivefolder)


