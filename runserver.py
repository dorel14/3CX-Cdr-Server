# -*- coding: UTF-8 -*-
import threading

from helpers.config import Config
from helpers.tcp_socket_server import serveur, traitementDonnées

HOST = ''
PORT = int(Config.get('TCP_SERVER', 'PORT'))

srv = None
threads = []


if __name__ == '__main__':
    srv = serveur(('', PORT), traitementDonnées)
    try:
        srv.server_bind()
        srv.server_activate()
        srv3cxon = threading.Thread(target=srv.serve_forever)
        srv3cxon.daemon = True
        srv3cxon.start()
        threads.append((srv3cxon, srv))
    except KeyboardInterrupt:
        def kill_me_please(server):
            for t, s in threads:
                s.server_close()
                s.shutdown()
            for t, s in threads:
                t.join()
            print('server down...')
        threading.Thread(target=kill_me_please, args=(srv,)).start()
        print("End")
