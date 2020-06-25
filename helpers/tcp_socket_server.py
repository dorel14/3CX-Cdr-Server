# -*- coding: utf-8 -*-

import socket
import socketserver
import threading

from helpers.cdr import parse_cdr


class traitementDonnées(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)
        return

    def handle(self):
        cdr = self.request.recv(2048)
        cdr = cdr.decode().strip()
        self.request.send(bytes(cdr, 'utf-8'))
        print(cdr)
        print(parse_cdr(cdr))
        if cdr == 'shutdown':
            self.request.close()
            threading.Thread(target=self.server.shutdown).start()
        self.request.close()
        return


class serveur(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass,
                                        bind_and_activate=False)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.socket.setblocking(0)
