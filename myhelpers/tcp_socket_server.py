# -*- coding: utf-8 -*-


import socketserver
import threading
import os
import sys
from setproctitle import setproctitle, getproctitle

from dotenv import load_dotenv
from .cdr import parse_cdr
from .logging import logger


class traitementDonnées(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)
        logger.info('handler init')
        return

    def handle(self):
        cdr = self.request.recv(2048)
        cdr = cdr.decode().strip()
        self.request.send(bytes(cdr, 'utf-8'))
        logger.info(cdr)
        logger.info(parse_cdr(cdr))
        if cdr == 'shutdown':
            self.request.close()
            threading.Thread(target=self.server.shutdown).start()
        self.request.close()
        return


class serveur(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass)

    def runserver():
        load_dotenv()
        HOST = '0.0.0.0'
        PORT = int(os.environ.get('SERVER_PORT'))
        tcpsrv = serveur((HOST, PORT), traitementDonnées)
        setproctitle('3cxtcpserver')
        log = 'Server loop ' + getproctitle() \
            + ' running in process: ' + str(os.getpid())
        print('Server loop ' + getproctitle() \
            + ' running in process: ' + str(os.getpid()))
        logger.info(log)
        try:
            tcpsrv.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
