# -*- coding: UTF-8 -*-
from scp import SCPClient
import paramiko
import os
import fnmatch
import socket
from time import sleep
from .logging import logger
from .traitement_fichier import csv_files_read

class scpclient():
    """
    Provides a class `scpclient` that handles connecting to an FTP server, downloading files that are newer than the local versions, and optionally archiving or deleting the downloaded files on the FTP server.
    """
    def __init__(self, host, user, password, port=22):
        """
        Initializes an instance of the `scpclient` class with the specified FTP server host, username, and password.
        """
        self.host=host
        self.user=user
        self.password=password
        self.port=port

    def monitor(self, ftpfolder='', localfolder='',archivefolder='', interval=50):
        """
        Monitors a remote directory via SCP/SSH, downloads new files, and processes them.

        This method establishes a secure SSH connection to the remote server, downloads
        files matching the pattern specified in the 3CX_FILEEXT environment variable,
        and then either archives or deletes the remote files based on configuration.

        Args:
            ftpfolder (str): Remote directory path to monitor
            localfolder (str): Local directory to download files to
            archivefolder (str): Directory to move processed files to
            interval (int): Time in seconds between monitoring cycles

        Returns:
            None
        """
        ssh = paramiko.SSHClient()

        try:
            # Use system host keys
            ssh.load_system_host_keys()

            # Or load from known_hosts file
            known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
            if os.path.exists(known_hosts_path):
                ssh.load_host_keys(known_hosts_path)

            # Reject unknown hosts by using the default policy
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

            # Connect with strict host key checking
            logger.info(f"Connecting to {self.host}:{self.port} as {self.user}")
            ssh.connect(
                hostname=self.host, 
                port=self.port, 
                username=self.user, 
                password=self.password, 
                banner_timeout=200
            )

            sftp = ssh.open_sftp()

            try:
                sftp.chdir(ftpfolder)
            except IOError as e:
                logger.error(f"Cannot access remote directory {ftpfolder}: {str(e)}")
                return

            fNames = sftp.listdir(sftp.getcwd())
            with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                for f in fNames:
                    logger.info(f"Found file: {f}")
                    scpfilename = os.path.join(ftpfolder, f)

                    # Only process files matching the configured pattern
                    if fnmatch.fnmatch(f, os.environ.get('3CX_FILEEXT')):
                        try:
                            # Check if file exists and is accessible
                            sftp.stat(scpfilename)

                            # Download the file
                            local_path = os.path.join(localfolder, f)
                            logger.info(f"Downloading file to {local_path}")
                            scp.get(remote_path=scpfilename, local_path=local_path)
                            logger.info("File downloaded successfully.")

                            # Archive or delete the remote file based on configuration
                            if os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'ARCHIVE':
                                try:
                                    sftp.rename(scpfilename, f"{scpfilename}.old")
                                    logger.info("Archived remote file")
                                except IOError as e:
                                    logger.error(f"Failed to archive remote file {scpfilename}: {str(e)}")
                            elif os.environ.get('3CX_FILES_ARCHIVE_OR_DELETE') == 'DELETE':
                                try:
                                    # Exécuter la commande sans sudo
                                    stdin, stdout, stderr = ssh.exec_command(f"rm -f {scpfilename}")
                                    exit_status = stdout.channel.recv_exit_status()
                                    if exit_status == 0:
                                        logger.info("Deleted remote file")
                                    else:
                                        error_output = stderr.read().decode('utf-8').strip()
                                        logger.error(f"Command failed with status {exit_status}: {error_output}")
                                except paramiko.SSHException as ssh_err:
                                    logger.error(f"SSH error while deleting {scpfilename}: {str(ssh_err)}")
                                except IOError as io_err:
                                    logger.error(f"I/O error while deleting remote file: {str(io_err)}")
                                except Exception as e:
                                    logger.error(f"Failed to delete remote file {scpfilename}: {str(e)}")
                        except IOError as e:
                            logger.warning(f"Cannot access remote file: {str(e)}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing remote file: {str(e)}")
                            continue

                # Process downloaded files
                try:
                    csv_files_read(localfolder, archivefolder)
                except Exception as e:
                    logger.error(f"Error processing downloaded files: {str(e)}")

                sleep(interval)

        except paramiko.ssh_exception.SSHException as e:
            logger.error(f"SSH connection error: {str(e)}")
            if "Host key verification failed" in str(e):
                logger.error(f"Host key verification failed for {self.host}. If this is a trusted host, add its key to known_hosts.")
            elif "Authentication failed" in str(e):
                logger.error(f"Authentication failed for user {self.user}. Please check credentials.")
            else:
                logger.error(f"SSH error: {str(e)}")
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            logger.error(f"Could not connect to {self.host}:{self.port}: {str(e)}")
        except socket.timeout:
            logger.error(f"Connection timeout while connecting to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Unexpected error in SCP monitor: {str(e)}")
        finally:
            # Ensure SSH connection is closed even if an exception occurs
            if ssh:
                ssh.close()
                logger.info("SSH connection closed")