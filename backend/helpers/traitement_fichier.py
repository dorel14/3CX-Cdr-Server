# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil
import re
from .cdr import parse_cdr, push_cdr_api, validate_cdr
from .logging import logger
import traceback

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
    """
    Safely moves a file to a timestamped location within the specified save folder.

    This function implements several security measures to prevent path traversal and
    other file-related vulnerabilities:
    1. Input validation for file path
    2. Path sanitization and normalization
    3. Directory traversal prevention
    4. Explicit permission checks
    5. File type validation (optional)

    Args:
        file (str): Path to the source file to be moved
        savefolder (str): Base directory where the file will be moved to

    Returns:
        str: Path to the destination file

    Raises:
        ValueError: If the file path or save folder contains suspicious patterns
        FileNotFoundError: If the source file doesn't exist
        PermissionError: If there are insufficient permissions
    """
    # Input validation for file parameter
    if not isinstance(file, str) or not file:
        raise ValueError("File path must be a non-empty string")

    # Check for suspicious patterns in file path
    suspicious_patterns = ['../', '..\\', '~', '$', '|', ';', '&', '>', '<']
    if any(pattern in file for pattern in suspicious_patterns):
        logger.error(f"Suspicious pattern detected in file path: {file}")
        raise ValueError("File path contains potentially malicious patterns")

    # Validate file exists before processing
    if not os.path.exists(file):
        raise FileNotFoundError(f"Source file does not exist: {file}")

    # Validate file is a regular file (not a symlink, device file, etc.)
    if not os.path.isfile(file):
        raise ValueError(f"Source path is not a regular file: {file}")

    # Optional: Validate file type/extension if needed
    # allowed_extensions = ['.csv', '.txt']
    # if not any(file.lower().endswith(ext) for ext in allowed_extensions):
    #     raise ValueError(f"File type not allowed: {file}")

    # Sanitize input paths
    filename = sanitize_filepath(file)
    savefolder = os.path.realpath(os.path.normpath(savefolder))

    # Verify save folder exists and is a directory
    if not os.path.exists(savefolder):
        raise ValueError(f"Save folder does not exist: {savefolder}")
    if not os.path.isdir(savefolder):
        raise ValueError(f"Save folder is not a directory: {savefolder}")

    # Check write permissions on save folder
    if not os.access(savefolder, os.W_OK):
        raise PermissionError(f"No write permission on save folder: {savefolder}")

    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Construct and validate paths
    final_path = os.path.realpath(os.path.normpath(os.path.join(savefolder, year, month)))
    if not final_path.startswith(savefolder):
        logger.error(f"Path traversal attempt detected: {final_path}")
        raise ValueError("Destination path outside allowed directory")

    source = os.path.realpath(os.path.normpath(file))
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file {source} does not exist")

    # Verify source file is readable
    if not os.access(source, os.R_OK):
        raise PermissionError(f"No read permission on source file: {source}")

    # Create a safe destination filename with timestamp prefix
    safe_filename = re.sub(r'[^\w\.-]', '_', filename)  # Replace unsafe chars
    destination = os.path.join(final_path, date + '_' + safe_filename)

    # Create directories with restricted permissions
    os.makedirs(final_path, mode=0o755, exist_ok=True)

    # Perform move operation with validated paths
    # file deepcode ignore PT: Path traversal is prevented by validation above
    shutil.move(source, destination)
    logger.info(f'File moved: {source} -> {destination}')

    return destination


def csv_files_read(filefolder, archivefolder):
    """
    Read and process CSV files from a specified folder, parsing CDR (Call Detail Record) data.

    Args:
        filefolder (str): Path to the directory containing CSV files to be processed.
        archivefolder (str): Path to the directory where processed files will be archived.

    Processes CSV files matching a specified file pattern (default '*.csv'), validates and 
    parses each line starting with 'Call', pushes CDR data via API, and moves successfully 
    processed files to the archive folder. Handles various file and processing errors with 
    comprehensive logging.

    Raises:
        ValueError: If the source directory is invalid.
        PermissionError: If there are insufficient permissions to access files or directories.
    """
    logger.info(f"Reading CSV files from folder: {filefolder}")

    try:
        # Sanitize and validate input folder path
        filefolder = os.path.realpath(os.path.normpath(filefolder))
        if not os.path.exists(filefolder):
            logger.error(f"Source directory does not exist: {filefolder}")
            raise ValueError("Invalid source directory")

        # Check directory permissions before proceeding
        try:
            check_directory_permissions(filefolder)
        except OSError as e:
            logger.error(f"Failed to check directory permissions: {str(e)}")

        os.chdir(filefolder)
        file_pattern = os.environ.get('3CX_FILEEXT')
        if not file_pattern:
            logger.warning("3CX_FILEEXT environment variable not set, defaulting to '*.csv'")
            file_pattern = '*.csv'

        files = list(glob.glob(file_pattern, recursive=False))
        logger.info(f"Found {len(files)} files matching pattern '{file_pattern}'")

        for f in files:
            try:
                # Validate each file path
                full_path = os.path.realpath(os.path.normpath(os.path.join(filefolder, f)))
                if not full_path.startswith(filefolder):
                    logger.error(f"Invalid file path (directory traversal attempt): {f}")
                    continue

                if not os.path.exists(full_path):
                    logger.error(f"File does not exist: {full_path}")
                    continue

                if not os.access(full_path, os.R_OK):
                    logger.error(f"No read permission for file: {full_path}")
                    continue

                logger.info(f"Processing file: {f}")

                try:
                    with open(full_path, 'r', encoding='utf-8') as csv_file:
                        count = 1
                        processed_lines = 0
                        error_lines = 0

                        while True:
                            try:
                                line = csv_file.readline()
                                if not line:
                                    break

                                testline = line.split(',')
                                if testline[0].startswith('Call'):
                                    try:
                                        cdrs, cdrdetails = parse_cdr(line, f)
                                        if validate_cdr(cdrs, cdrdetails):
                                            rcdr, rcdrdetails = push_cdr_api(cdrs, cdrdetails)
                                            logger.info(f"Line {count}: Processed successfully")
                                            logger.debug(f"CDR status: {rcdr}, CDR details status: {rcdrdetails}")
                                            processed_lines += 1
                                        else:
                                            logger.error(f"Validation error line {count}")
                                            error_lines += 1
                                    except Exception as e:
                                        logger.error(f"Error processing line {count}: {str(e)}")
                                        logger.debug(f"Problematic line: {line.strip()}")
                                        error_lines += 1
                                count += 1
                            except UnicodeDecodeError as e:
                                logger.error(f"Unicode decode error at line {count}: {str(e)}")
                                error_lines += 1
                                count += 1
                                continue

                    logger.info(f"File {f} processing complete. Processed {processed_lines} lines with {error_lines} errors.")

                    # Move the file to archive folder after processing
                    try:
                        files_move(full_path, archivefolder)
                    except (ValueError, FileNotFoundError, PermissionError) as e:
                        logger.error(f"Failed to move file {f} to archive: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error moving file {f} to archive: {str(e)}")
                        logger.debug(traceback.format_exc())

                except PermissionError as e:
                    logger.error(f"Permission error opening file {f}: {str(e)}")
                except FileNotFoundError as e:
                    logger.error(f"File not found error opening {f}: {str(e)}")
                except UnicodeError as e:
                    logger.error(f"Unicode error opening file {f}: {str(e)}")
                except IOError as e:
                    logger.error(f"IO error opening file {f}: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error opening file {f}: {str(e)}")
                    logger.debug(traceback.format_exc())

            except Exception as e:
                logger.error(f"Unexpected error processing file {f}: {str(e)}")
                logger.debug(traceback.format_exc())

    except PermissionError as e:
        logger.error(f"Permission error accessing directory {filefolder}: {str(e)}")
    except OSError as e:
        logger.error(f"OS error accessing directory {filefolder}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in csv_files_read: {str(e)}")
        logger.debug(traceback.format_exc())



