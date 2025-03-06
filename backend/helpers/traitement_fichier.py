# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil

from .cdr import parse_cdr, push_cdr_api, validate_cdr
from .logging import logger


def sanitize_filepath(filepath):
    # Nettoie le chemin en ne gardant que le nom de base du fichier
    return os.path.basename(os.path.normpath(filepath))

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
    # Sanitize input paths
    filename = sanitize_filepath(file)
    savefolder = os.path.realpath(os.path.normpath(savefolder))
    
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    
    # Construct and validate paths
    final_path = os.path.realpath(os.path.normpath(os.path.join(savefolder, year, month)))
    if not final_path.startswith(savefolder):
        raise ValueError("Destination path outside allowed directory")
    
    source = os.path.realpath(os.path.normpath(file))
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file {source} does not exist")
        
    destination = os.path.join(final_path, date + '_' + filename)
    
    # Create directories with restricted permissions
    os.makedirs(final_path, mode=0o755, exist_ok=True)
    
    # Perform move operation with validated paths
    # file deepcode ignore PT: <please specify a reason of ignoring this>
    shutil.move(source, destination)
    logger.info(f'File moved: {source} -> {destination}')


def csv_files_read(filefolder, archivefolder):
    logger.info(filefolder)
    
    # Sanitize and validate input folder path
    filefolder = os.path.realpath(os.path.normpath(filefolder))
    if not os.path.exists(filefolder):
        raise ValueError("Invalid source directory")
        
    os.chdir(filefolder)
    file_pattern = os.environ.get('3CX_FILEEXT')
    
    for f in list(glob.glob(file_pattern, recursive=False)):
        # Validate each file path
        full_path = os.path.realpath(os.path.normpath(os.path.join(filefolder, f)))
        if not full_path.startswith(filefolder):
            logger.error(f"Invalid file path: {f}")
            continue
            
        with open(full_path, 'r', encoding='utf-8') as csv:
            count = 1
            while True:            
                line = csv.readline()
                if not line:
                    break
                testline = line.split(',')
                if testline[0].startswith('Call'):
                    cdrs, cdrdetails = parse_cdr(line, f)
                    if validate_cdr(cdrs, cdrdetails):
                        rcdr, rcdrdetails = push_cdr_api(cdrs, cdrdetails)
                        logger.info(rcdr)
                        logger.info(rcdrdetails)
                        logger.info(f"Line{count}: {line.strip()}")
                        count += 1
                    else:
                        logger.error(f"Validation error line: {count} \n {line.strip()}")
                        
        files_move(full_path, archivefolder)


