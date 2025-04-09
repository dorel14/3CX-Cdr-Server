# -*- coding: UTF-8 -*-
import socketserver
import os
import json
from setproctitle import setproctitle
from ..helpers.logging import logger
from ..helpers.cdr import push_cdr_api, push_cdr_api2, validate_cdr

class traitementDonnées(socketserver.BaseRequestHandler):
    """
    The `traitementDonnées` class is a request handler for the TCP server. It inherits from `socketserver.BaseRequestHandler` and is responsible for processing incoming TCP connections and the data received from clients.
    """
    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request,
                                                client_address, server)

    def handle(self):
        """
        Handles incoming TCP connections and processes the received data.
        """
        try:
            # Lire les données du client
            cdr = self.request.recv(8192)

            # Si les données sont vides ou contiennent juste "HEALTHCHECK", c'est un healthcheck
            if not cdr or cdr.strip() == b'HEALTHCHECK':
                # Optionnellement, envoyer une réponse de confirmation
                self.request.sendall(b'OK\r\n')
                return

            # Continuer avec le traitement normal des données
            cdr_encoding = os.environ.get('CDR_ENCODING', 'utf-8')
            cdr = cdr.decode(encoding=cdr_encoding).strip()
            logger.info(f"Données reçues: {cdr[:100]}...")  # Log only the first 100 chars

            try:
                # Tentative de décodage JSON
                cdr_json = json.loads(cdr)

                # Vérification si c'est un CDR ou un CDR_DETAILS
                if 'historyid' in cdr_json:
                    # C'est un CDR
                    logger.info("Données CDR reçues")
                    # Traitement du CDR
                    # ...
                elif 'cdr_historyid' in cdr_json:
                    # C'est un CDR_DETAILS
                    logger.info("Données CDR_DETAILS reçues")
                    # Traitement du CDR_DETAILS
                    # ...
                else:
                    logger.warning("Format de données inconnu")
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, traiter comme avant
                logger.info("Traitement des données non-JSON")
                # Traitement des données non-JSON
                # ...

        except Exception as e:
            logger.error(f"Erreur lors du traitement de la connexion: {str(e)}")


class serveur(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    The `serveur` class is a custom TCP server implementation that inherits from `socketserver.ThreadingMixIn` and `socketserver.TCPServer`. It is designed to handle incoming TCP connections and process data received from clients.

    The class has the following configuration options:
    - `daemon_threads`: When set to `True`, the server will automatically clean up all spawned threads when the main process exits.
    - `allow_reuse_address`: When set to `True`, the server will allow the reuse of the same address and port, which can speed up the process of rebinding the server.

    The `runserver()` function is responsible for starting the TCP server. It loads environment variables, sets the server address and port, creates an instance of the `serveur` class, sets the process title, and logs the server's running status. The server is then started using the `serve_forever()` method, which will block until the server is stopped (e.g., by a keyboard interrupt).
    """

    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

    def __init__(self, server_address, handler_class):
        super().__init__(server_address, handler_class)


    @classmethod
    def runserver(cls, host, port):
        """
        The `runserver()` function is responsible for starting the TCP server. It loads environment variables, sets the server address and port, creates an instance of the `serveur` class, sets the process title, and logs the server's running status. The server is then started using the `serve_forever()` method, which will block until the server is stopped (e.g., by a keyboard interrupt).
        """
        setproctitle('3cxtcpserver')
        logger.info(f'Server running in process: {os.getpid()}')

        with cls((host, port), traitementDonnées) as server:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Serveur arrêté par l'utilisateur")
                server.shutdown()