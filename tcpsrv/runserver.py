# -*- coding: UTF-8 -*-
import os
import sys
from setproctitle import setproctitle, getproctitle

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from helpers.tcp_socket_server import serveur, traitementDonnées
from helpers.logging import logger

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
