# -*- coding: UTF-8 -*-
import glob
import os
from gettext import gettext as _
from datetime import datetime
import shutil

from myhelpers.cdr import parse_cdr, push_cdr_api
from myhelpers.logging import logger

#filefolder = '/opt/cdrfiles'
#savefolder = '/opt/cdrfiles_archives'

def check_directory_permissions(directory_path):
    permissions = os.stat(directory_path).st_mode
    logger.error(f"Permissions of the directory:{directory_path}")
    logger.error(f"Read permission: {'Yes' if permissions & 0o400 else 'No'}")
    logger.error(f"Write permission: {'Yes' if permissions & 0o200 else 'No'}")
    logger.error(f"Execute permission: {'Yes' if permissions & 0o100 else 'No'}")

def files_move(file, savefolder):
    filename = str(os.path.basename(file))
    logger.info(filename)
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    check_directory_permissions(savefolder)
    if not os.path.exists(savefolder):
        os.mkdir(savefolder, mode=0o777)
    savefolderd = os.path.join(savefolder, year)
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd, mode=0o777)
    savefolderd = os.path.join(savefolderd, month)
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd, mode=0o777)
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


