#!/bin/bash

WDIR=/home/cdrTcpServer
VIRTUALENV_DIR=/home/cdrTcpServer/env

cd $WDIR
source $VIRTUALENV_DIR/bin/activate


   if [ -e /var/run/cdrserver.pid ]; then

      rm /var/run/cdrserver.pid

   fi



python runserver.py 1> /var/log/supportbot/debugTCPSERVER.log  & 2> /var/log/supportbot/error_TCPSERVER.log
#pgrep 3cxtcpserver > /var/run/cdrserver.pid
