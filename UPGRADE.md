# Upgrade Instructions

## Overview

This document explains the purpose of the update scripts and how to use them based on your operating system. The update scripts are designed to help you safely upgrade your 3CX CDR Server application by performing the following tasks:

1. Backing up the database.
2. Detecting and moving renamed files.
3. Resetting the master branch to the latest version.
4. Cleaning up obsolete files.
5. Rebuilding the environment.

## Important Notice

**This new version introduces significant changes. It is crucial to back up your data before updating.**

## Update Scripts

### Linux / macOS

For Linux and macOS users, use the `update.sh` script.

#### Usage (Linux / macOS)

1. Open a terminal.
2. Navigate to the project directory.
3. Make the script executable:

    ```sh
    chmod +x update.sh
    ```

4. Run the following command:

    ```sh
    ./update.sh
    ```

### Windows (PowerShell)

For Windows users using PowerShell, use the `update.ps1` script.

#### Usage (PowerShell)

1. Open PowerShell as an administrator.
2. Navigate to the project directory.
3. Run the following command:

    ```powershell
    ./update.ps1
    ```

### Windows (Batch)

For Windows users using Command Prompt, use the `update.bat` script.

#### Usage (Batch)

1. Open Command Prompt as an administrator.
2. Navigate to the project directory.
3. Run the following command:

    ```bat
    update.bat
    ```

## Detailed Steps

### 1. Backing up the Database

The scripts will create a backup of your PostgreSQL database using the `pg_dump` command. The backup file will be saved as `backup.sql` in the project directory.

### 2. Detecting and Moving Renamed Files

The scripts will detect any renamed files using `git diff` and move them to their new locations.

### 3. Resetting the Master Branch

The scripts will reset the master branch to the latest version from the remote repository using `git fetch`, `git checkout`, and `git reset`.

### 4. Cleaning Up Obsolete Files

The scripts will clean up any obsolete files using `git clean`.

### 5. Rebuilding the Environment

The scripts will rebuild the Docker environment using `docker-compose down` and `docker-compose up -d --build`.

## Conclusion

By following these instructions, you can safely upgrade your 3CX CDR Server application to the latest version. If you encounter any issues, please refer to the project's wiki or create an issue on [GitHub](https://github.com/dorel14/3CX-Cdr-Tcp-Server/issues).
