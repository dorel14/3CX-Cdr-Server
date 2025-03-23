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
    Checks and logs the permissions of the specified directory path to ensure proper file operations.

    This function examines the read, write, and execute permissions of a directory, as well as
    its ownership information (user and group IDs). These permission checks are critical for
    the application's file handling operations, particularly for:

    1. File Movement: When moving files between directories using files_move(), the application
    needs write permissions in both source and destination directories.

    2. CSV Processing: When reading and processing CSV files with csv_files_read(), the application
    requires read permissions on the source directory and files.

    3. Archive Operations: When creating archive directories with year/month structure, the application
    needs execute and write permissions to create subdirectories.

    4. Security: Logging ownership information helps identify potential permission issues related
    to user/group access, especially in containerized environments where UID/GID mapping
    can cause unexpected behavior.

    The function logs all permission information at ERROR level to ensure visibility during
    troubleshooting, even when normal logging is set to a higher threshold.

    Args:
        directory_path (str): The absolute path to the directory whose permissions should be checked

    Returns:
        None: Results are logged but not returned

    Raises:
        OSError: If the directory does not exist or cannot be accessed
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


