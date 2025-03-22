# -*- coding: utf-8 -*-
import os
import logging
import pathlib
import stat
from datetime import datetime
from logging.handlers import RotatingFileHandler

date_format = "%Y%m%d"
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
logdir = os.path.join(parentdir, './logs')
logfiles = os.path.join(logdir, '3cxtcpserver'+ datetime.today().strftime(date_format) +'.log')

pathlib.Path(logdir).mkdir(parents=True, exist_ok=True)
# Définir les permissions du répertoire de logs (777 = rwxrwxrwx)
try:
    os.chmod(logdir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # équivalent à 0o777
    print(f"Permissions du répertoire {logdir} modifiées avec succès")
except Exception as e:
    print(f"Impossible de modifier les permissions du répertoire {logdir}: {e}")

# Créer le fichier de log s'il n'existe pas et définir ses permissions
if not os.path.exists(logfiles):
    try:
        # Créer un fichier vide
        with open(logfiles, 'a'):
            pass
        # Définir les permissions du fichier (666 = rw-rw-rw-)
        os.chmod(logfiles, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)  # équivalent à 0o666
        print(f"Fichier {logfiles} créé avec les permissions appropriées")
    except Exception as e:
        print(f"Impossible de créer ou de modifier les permissions du fichier {logfiles}: {e}")

# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
file_handler = RotatingFileHandler(filename=logfiles,
                                   mode='a',
                                   maxBytes=1000000,
                                   backupCount=5)
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(getattr(logging, log_level))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# création d'un second handler qui va rediriger chaque écriture de log
# sur la console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(getattr(logging, log_level))
logger.addHandler(stream_handler)
