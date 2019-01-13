#!/bin/sh
### BEGIN INIT INFO
# Provides:
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:     Starts graphite-beacon using start-stop-daemon 
### END INIT INFO

#PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
PATH=$PATH
DAEMON=/usr/local/bin/graphite-beacon
CONF=/etc/graphite-beacon/config.json
LOG=/mnt/log/beacon/graphite-beacon.log
ERR_LOG=/mnt/log/beacon/graphite-beacon.err
PID=/var/run/graphite-beacon.pid


test -e $CONF ||exit 1
test -x $DAEMON || exit 1
test -e $LOG ||exit 1
test -e $ERR_LOG ||exit 1


. /lib/init/vars.sh
. /lib/lsb/init-functions


case $1 in

  start) 
	[ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
    if [ $? -ne 0 ];then
        log_daemon_msg "Starting graphite beacon" "graphite-beacon" || true		
	    if start-stop-daemon --start --quiet -b  --make-pidfile --pid $PID --exec $DAEMON -- --config=$CONF  --log_file_prefix=$LOG 2>>$ERR_LOG ;then
    	    [ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
            if [ $? -eq 0 ];then
	    	    log_end_msg 0 || true	
            else
		        log_failure_msg "Fail to start graphite-beacon, see error log in $ERR_LOG" || true
            fi
	    else
		    log_failure_msg "Fail to start graphite-beacon, see error log in $ERR_LOG" || true
	    fi
    else
        log_failure_msg "Graphite beacon already run" || true 
    fi
	;;

  stop)
	[ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
    if [ $? -eq 0 ];then
	    log_daemon_msg "Stopping graphite beacon" "graphite-beacon" || true
    	if start-stop-daemon --stop --quiet  --pidfile $PID 2>>$ERR_LOG;then
	    	log_end_msg 0 || true
    	else
            log_failure_msg "Fail to stop graphite-beacon, see error log in $ERR_LOG" || true 
    	fi
    else 
        log_failure_msg "Graphite beacon already stop" || true 
	fi
	;;

  status)
	[ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
	if [ $? -eq 0 ];then
		echo "Running"
	else
		echo "Stopped"
		exit 1
	fi
	;;

  restart|force-reload)
	[ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
    if [ $? -eq 0 ];then 
    	    log_daemon_msg "Restarting graphite beacon" "graphite-beacon" || true
	        start-stop-daemon --stop --quiet  --retry 30 --pidfile $PID 2>>$ERR_LOG
            if [ $? -eq 0 ];then
    	        sleep 1
        	    if start-stop-daemon --start --quiet -b  --make-pidfile --pid $PID --exec $DAEMON -- --config=$CONF --log_file_prefix=$LOG 2>>$ERR_LOG;then
                    [ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
                 if [ $? -eq 0 ];then
	    	            log_end_msg 0 || true	
                    else
	    	            log_failure_msg "Fail to start graphite-beacon, see error log in $ERR_LOG" || true
                    fi
                else
                    log_failure_msg "Fail to restart graphite-beacon, see error log in $ERR_LOG" || true 
                fi
            else
                
                    log_failure_msg "Fail to restart graphite-beacon, see error log in $ERR_LOG" || true 
            fi
    else
        log_action_msg "Graphite-beacon doesn't start, start it now"
    	if start-stop-daemon --start --quiet  --make-pidfile -b --pid $PID --exec $DAEMON -- --config=$CONF --log_file_prefix=$LOG 2>>$ERR_LOG;then
            [ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
            if [ $? -eq 0 ];then
	    	    log_end_msg 0 || true	
            else
		        log_failure_msg "Fail to start graphite-beacon, see error log in $ERR_LOG" || true
            fi

        else
            log_failure_msg "Fail to restart graphite-beacon, see error log in $ERR_LOG" || true 
        fi
    fi
	;;
  
  reload)
	[ -f "$PID" ] && ps `cat $PID` > /dev/null 2>&1
    if [ $? -eq 0 ];then 
	    log_daemon_msg "Reloading graphite beacon" "graphite-beacon" || true
    	if start-stop-daemon --stop --signal HUP --quiet  --pidfile $PID  2>>$ERR_LOG; then
                log_end_msg 0 || true
        else
                log_failure_msg "Fail to reload graphite-beacon, see error log in $ERR_LOG" || true
        fi
    else
        log_failure_msg "Graphite-beacon doesn't start, you must start it firstly"
    fi
	;;
  *)
	log_action_msg "Usage: /etc/init.d/graphite-beacon {start|stop|reload|force-reload|restart|status}" || true
        exit 1

esac

exit 0

