# Instructions de Mise à Jour

## Vue d'ensemble

Ce document explique l'objectif des scripts de mise à jour et comment les utiliser en fonction de votre système d'exploitation. Les scripts de mise à jour sont conçus pour vous aider à mettre à jour en toute sécurité votre application 3CX CDR Server en effectuant les tâches suivantes :

1. Sauvegarde de la base de données.
2. Détection et déplacement des fichiers renommés.
3. Réinitialisation de la branche master à la dernière version.
4. Nettoyage des fichiers obsolètes.
5. Reconstruction de l'environnement.

## Avis Important

**Cette nouvelle version introduit des changements importants. Il est crucial de sauvegarder vos données avant de mettre à jour.**

## Scripts de Mise à Jour

### Linux / macOS

Pour les utilisateurs de Linux et macOS, utilisez le script `update.sh`.

#### Utilisation

1. Ouvrez un terminal.
2. Naviguez jusqu'au répertoire du projet.
3. Rendez le script exécutable :
    ```sh
    chmod +x update.sh
    ```
4. Exécutez la commande suivante :
    ```sh
    ./update.sh
    ```

### Windows (PowerShell)

Pour les utilisateurs de Windows utilisant PowerShell, utilisez le script `update.ps1`.

#### Utilisation

1. Ouvrez PowerShell en tant qu'administrateur.
2. Naviguez jusqu'au répertoire du projet.
3. Exécutez la commande suivante :
    ```powershell
    ./update.ps1
    ```

### Windows (Batch)

Pour les utilisateurs de Windows utilisant l'invite de commandes, utilisez le script `update.bat`.

#### Utilisation

1. Ouvrez l'invite de commandes en tant qu'administrateur.
2. Naviguez jusqu'au répertoire du projet.
3. Exécutez la commande suivante :
    ```bat
    update.bat
    ```

## Étapes Détailées

### 1. Sauvegarde de la Base de Données

Les scripts créeront une sauvegarde de votre base de données PostgreSQL en utilisant la commande `pg_dump`. Le fichier de sauvegarde sera enregistré sous le nom `backup.sql` dans le répertoire du projet.

### 2. Détection et Déplacement des Fichiers Renommés

Les scripts détecteront tous les fichiers renommés en utilisant `git diff` et les déplaceront vers leurs nouveaux emplacements.

### 3. Réinitialisation de la Branche Master

Les scripts réinitialiseront la branche master à la dernière version du dépôt distant en utilisant `git fetch`, `git checkout` et `git reset`.

### 4. Nettoyage des Fichiers Obsolètes

Les scripts nettoieront tous les fichiers obsolètes en utilisant `git clean`.

### 5. Reconstruction de l'Environnement

Les scripts reconstruiront l'environnement Docker en utilisant `docker-compose down` et `docker-compose up -d --build`.

## Conclusion

En suivant ces instructions, vous pouvez mettre à jour en toute sécurité votre application 3CX CDR Server vers la dernière version. Si vous rencontrez des problèmes, veuillez consulter le wiki du projet ou créer une issue sur [GitHub](https://github.com/dorel14/3CX-Cdr-Tcp-Server/issues).
