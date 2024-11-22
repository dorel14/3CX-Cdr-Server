# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil

from helpers.cdr import parse_cdr, push_cdr_api, validate_cdr
from helpers.logging import logger

#filefolder = '/opt/cdrfiles'
#savefolder = '/opt/cdrfiles_archives'

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
    """
    Moves a file to an archive folder, creating the necessary directory structure based on the current date.
    
    Args:
        file (str): The path to the file to be moved.
        savefolder (str): The path to the archive folder where the file will be moved.
    
    Raises:
        ValueError: If the final path for the file is not within the specified archive folder.
    
    Returns:
        None
    """
        # Nettoyer le nom du fichier
    filename = sanitize_filepath(file)
    # Nettoyer le chemin du dossier de sauvegarde
    savefolder = os.path.abspath(savefolder)
    
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    
    # Vérifier que le chemin final reste dans le dossier prévu
    final_path = os.path.join(savefolder, year, month)
    if not os.path.commonprefix([os.path.abspath(final_path), savefolder]) == savefolder:
        raise ValueError("Chemin de destination invalide")
        
    # Création des dossiers avec vérification
    for folder in [savefolder, os.path.join(savefolder, year), final_path]:
        if not os.path.exists(folder):
            os.makedirs(folder, mode=0o777)
        check_directory_permissions(folder)
    
    # Déplacement sécurisé du fichier
    source = os.path.abspath(file)
    destination = os.path.join(final_path, date + '_' + filename)
    shutil.move(source, destination)
    logger.info(f'{source} déplacé vers {destination}')

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
                if validate_cdr(cdrs, cdrdetails):
                    rcdr, rcdrdetails = push_cdr_api(cdrs, cdrdetails)
                    logger.info(rcdr)
                    logger.info(rcdrdetails)
                    logger.info("Line{}: {}".format(count, line.strip()))
                    count += 1
                    pass
                else:
                    logger.error(f"Erreur de validation ligne: {count} \n {line.strip()}")
        csv.close()
        files_move(f, archivefolder)


