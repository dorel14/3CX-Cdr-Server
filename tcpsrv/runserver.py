# -*- coding: UTF-8 -*-
import os
import sys


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


from helpers.tcp_socket_server import serveur

if __name__ == '__main__':
    serveur.runserver()
