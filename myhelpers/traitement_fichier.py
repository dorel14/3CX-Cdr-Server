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
    """
    Checks the permissions of the specified directory path and logs the read, write, and execute permissions, as well as the user and group ownership.
    
    This function is used to ensure that the necessary permissions are set on directories used for file operations, such as creating new directories or moving files.
    """
    permissions = os.stat(directory_path).st_mode
    logger.error(f"Permissions of the directory:{directory_path}")
    logger.error(f"Read permission: {'Yes' if permissions & 0o400 else 'No'}")
    logger.error(f"Write permission: {'Yes' if permissions & 0o200 else 'No'}")
    logger.error(f"Execute permission: {'Yes' if permissions & 0o100 else 'No'}")
    logger.error(f"User : {os.stat(directory_path).st_uid}")
    logger.error(f"Group : {os.stat(directory_path).st_gid}")

def files_move(file, savefolder):
    """
    Moves a file to a specified save folder, creating the necessary directory structure if it doesn't exist.
    
    This function is used to archive files by moving them to a designated save folder, organizing them by year and month. It checks the permissions of the save folder and any newly created subdirectories to ensure the necessary read, write, and execute permissions are set.
    
    Args:
        file (str): The path of the file to be moved.
        savefolder (str): The base directory where the file will be moved to.
    
    Returns:
        None
    """
    filename = str(os.path.basename(file))
    logger.info(filename)
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")    
    if not os.path.exists(savefolder):
        os.mkdir(savefolder, mode=0o777)
    check_directory_permissions(savefolder)
    savefolderd = os.path.join(savefolder, year)
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd, mode=0o777)
    check_directory_permissions(savefolderd)
    savefolderd = os.path.join(savefolderd, month)
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd, mode=0o777)
    check_directory_permissions(savefolderd)
    shutil.move(file, os.path.join(savefolderd, date + '_' + filename))  # to move files from
    logger.info(file + ' moved')

def csv_files_read(filefolder, archivefolder):
    """
    Reads and processes CSV files from a specified folder, parsing the CDR (Call Detail Record) data and pushing it to an API. The processed files are then moved to an archive folder.
    
    Args:
        filefolder (str): The path to the folder containing the CSV files to be processed.
        archivefolder (str): The path to the folder where the processed files will be moved.
    
    Returns:
        None
    """
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


