# -*- coding: utf-8 -*-

import socketserver
import threading
import os

import chardet
from setproctitle import setproctitle


from .cdr import parse_cdr, push_cdr_api
from .logging import logger


class traitementDonnées(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request,
                                                client_address, server)
        logger.info('handler init')
        return

    def handle(self):
        cdr = self.request.recv(2048)
        cdr_encoding = chardet.detect(cdr).get('encoding')
        logger.debug(cdr_encoding)
        cdr = cdr.decode(encoding=cdr_encoding).strip()
        self.request.send(bytes(cdr, 'utf-8'))
        
        logger.info(cdr)
        

        #webapi_url_cdr = os.environ.get('API_URL') + '/api/v1/cdr'
        cdrs, cdrdetails = parse_cdr(cdr)
        rcdr, rcdrdetails = push_cdr_api(cdrs, cdrdetails)
        print(rcdr, rcdrdetails)

        if cdr == 'shutdown':
            self.request.close()
            shutdown_thread = threading.Thread(target=self.server.shutdown)
            shutdown_thread.start()
            shutdown_thread.join()
        self.request.close()
        return


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
                server.shutdown()