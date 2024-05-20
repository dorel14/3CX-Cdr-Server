
# Multilanguage README Pattern
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)
# Enregistrement des CDR 3CX dans une base de données PostgreSql avec Grafana

## Description
Cet outil permet l'enregistrement des CDR 3CX dans une base de données PostgreSql et la création de tableaux de bord avec l'outil Grafana.

## Installation
Pour bénéficier de l'ensemble des fonctions, il est nécessaire de faire l'installation via Docker. Cette image contient 5 conteneurs :
- Serveur TCP / Client FTP - SFTP - SCP
- Serveur webapi
- Conteneur Postgres v12
- Conteneur PgAdmin
- Conteneur Grafana pour les dashboards

## Configuration
1. Les paramètres de base doivent être renseignés dans un fichier `.env` à la racine du répertoire selon le modèle `.env_template`.
2. Les paramétrages doivent être faits sur le serveur 3CX comme indiqué ci-dessous :
</br><a href="https://www.3cx.com/docs/cdr-call-data-records">Paramétrage des CDR</a>

### Paramétrage des CDR dans 3CX :
- Pour un tansfert via TCP : assurez-vous d'indiquer "3CX CDR service is client / Active Socket" afin que le serveur 3CX se connecte sur notre serveur TCP.
- Pour un transfert via FTP/SFTP/SCP: assurez-vous de générer des fichiers . Je vous conseille de générer 1 fichier par appel afin que ceux-ci soient intégrés au fil de la journée .
Attention ce mode de fonctionnement nécéssite de mettre en place un serveur FTP dans lequel les fichiers CDR seront disponibles et que ce serveur soit accessible par l'application.
Dans le fichier de paramétrage , vous pouvez choisir d'archiver les fichiers sur le serveur FTP , ils seront renommer en .old , ou de les supprimer.
Dans tout les cas ,  les fichiers sont sauvegardés après traitement dans le dossier LOCAL_CDR_FOLDER_ARCHIVE indiqué dans le fichier .env et monté sur le serveur éxécutant la stack Docker.

- Le paramétrage des CDR dans 3CX doit suivre cet ordre :
<ul>
<li>historyid</li>
<li>callid</li>
<li>duration</li>
<li>time_start</li>
<li>time_answered</li>
<li>time_end</li>
<li>reason_terminated</li>
<li>from_no</li>
<li>to_no</li>
<li>from_dn</li>
<li>to_dn</li>
<li>dial_no</li>
<li>reason_changed</li>
<li>final_number</li>
<li>final_dn</li>
<li>bill_code</li>
<li>bill_rate</li>
<li>bill_cost</li>
<li>bill_name</li>
<li>chain</li>
<li>from_type</li>
<li>to_type</li>
<li>final_type</li>
<li>from_dispname</li>
<li>to_dispname</li>
<li>final_dispname</li>
<li>missed_queue_calls</li>
</ul>

Journaux:
Les fichiers de log sont dans le dossier : /home/appuser/app/logs


### Contributions
Si vous appréciez mon travail n'hésitez à [m'offrir un café , une bière ou toute autre boisson](https://buymeacoffee.com/dorel14)
