#!/bin/bash
# run this as the rhodecode user!

WDIR=/home/cdrTcpServer
VIRTUALENV_DIR=/home/cdrTcpServer/env

cd $WDIR
source $VIRTUALENV_DIR/bin/activate


   if [ -e /var/run/cdrserver.pid ]; then

      rm /var/run/cdrserver.pid

   fi



python runserver.py 1> /var/log/supportbot/debugTCPSERVER-$(date +"%d_%m_%Y_%H_%M_%p").log  &
pgrep 3cxtcpserver > /var/run/cdrserver.pid
