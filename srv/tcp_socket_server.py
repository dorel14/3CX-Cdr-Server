# -*- coding: utf-8 -*-

import socketserver
import threading
import os
import sys
import chardet
from setproctitle import setproctitle, getproctitle

from dotenv import load_dotenv
import requests
from myhelpers.cdr import parse_cdr, push_cdr_api
from myhelpers.logging import logger


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
