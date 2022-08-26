# -*- coding: UTF-8 -*-
import os
import sys


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


if __name__ == '__main__':
    from helpers.tcp_socket_server import serveur
    serveur.runserver()
