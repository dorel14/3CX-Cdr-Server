# -*- coding: UTF-8 -*-
import threading
import os
import sys
from setproctitle import setproctitle, getproctitle

from app.helpers.tcp_socket_server import serveur, traitementDonnées
from app.helpers.logging import logger

HOST = '0.0.0.0'
PORT = int(os.environ.get('SERVER_PORT'))

if __name__ == '__main__':
    tcpsrv = serveur((HOST, PORT), traitementDonnées)
    setproctitle('3cxtcpserver')
    log = 'Server loop ' + getproctitle() \
        + ' running in process: ' + str(os.getpid())
    logger.info(log)
    try:
        tcpsrv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
