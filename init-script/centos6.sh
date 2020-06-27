#!/bin/bash

#
# example start stop daemon for CentOS (sysvinit)
#
# chkconfig: - 64 36
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 2 3 4 6
# Required-Start:
# description: example start stop daemon for CentOS
# processname: slack-machine
# pidfile: none
# lockfile: /var/lock/subsys/example

# Source function library.
. /etc/rc.d/init.d/functions

# Source networking configuration.
. /etc/sysconfig/network

# Check that networking is up.
DAEMON_NAME=3cxtcpserver
SERVER_PID=/var/run/cdrserver.pid
PIDFILE=/var/run/$DAEMON_NAME.pid

case "$1" in

start)

   /home/cdrTcpServer/init-script/cdrserverstart.sh &

   echo $!>$PIDFILE
   echo 'Server started'

   ;;

stop)

   kill $(cat $SERVER_PID)
   kill $(cat $PIDFILE)
   rm $PIDFILE
   rm $SERVER_PID
   echo 'Server stopped'
   ;;

restart)

   $0 stop

   $0 start

   ;;

status)

   if [ -e $PIDFILE ]; then

      echo $DAEMON_NAME & 'is running, pid= ' $(cat $SERVER_PID)

   else

      echo $DAEMON_NAME  ' is NOT running '

      exit 1

   fi

   ;;

*)

   echo "Usage: $0 {start|stop|status|restart}"

esac



exit 0


