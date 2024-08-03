
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dorel14/3CX-Cdr-Tcp-Server/blob/master/README.md)

# Enregistrement des CDR 3CX dans une base de données PostgreSQL avec Grafana

## Description

Cet outil facilite l'enregistrement des CDR (Call Detail Records) de 3CX dans une base de données PostgreSQL et la création de tableaux de bord avec Grafana.

Il permet de collecter les données d'appels de votre système de téléphonie 3CX et de les stocker dans une base de données PostgreSQL. Grâce à Grafana, vous pouvez ensuite visualiser ces données sous forme de tableaux de bord interactifs et personnalisables.

## Fonctionnalités principales

- **Collecte des CDR** : Récupération des CDR de 3CX via différents modes de transfert (TCP, FTP, SFTP, SCP).
- **Intégration d'informations 3cx** : Les extensions et les files d'attentes (queues) peuvent être intégrées en base de données via l'interface web disponible afin de permettre des analyses plus fines des CDR
- **Stockage dans PostgreSQL** : Enregistrement des CDR dans une base de données PostgreSQL pour un stockage centralisé et structuré.
- **API Web** : Une API Web est fournie pour interagir avec les données de CDR stockées.
- **Visualisation avec Grafana** : Création de tableaux de bord Grafana pour visualiser et analyser les données d'appels de manière interactive.

## Technologies utilisées

- Python
- FastAPI (API Web)
- PostgreSQL (Base de données)
- Grafana (Visualisation de données)
- Docker (Conteneurisation)

## Contributions

Si vous appréciez ce projet et souhaitez contribuer, n'hésitez pas à soumettre des pull requests ou à signaler des problèmes. Toute contribution est la bienvenue !

Pour plus d'informations sur l'installation, la configuration et l'utilisation de cet outil, veuillez consulter le wiki du projet.
