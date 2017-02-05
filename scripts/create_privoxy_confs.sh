#!/bin/bash
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
ETCBASE="/etc/privoxy"
LOGBASE="/var/log/privoxy"
SOCKSBASE=9050
LISTENBASE=3128
N_INSTANCES=8
for ((INSTANCE=1;INSTANCE<=8;INSTANCE++))
do
	
	CONFDIR="$ETCBASE$INSTANCE"	
	LOGDIR="$LOGBASE$INSTANCE"
	chown privoxy $LOGDIR
	chgrp adm $LOGDIR
	CONF="$CONFDIR/config"
	SOCKS_PORT=$((SOCKSBASE+INSTANCE))
    LISTEN_PORT=$((LISTENBASE+INSTANCE))
    echo "Configuring instance $INSTANCE with $SOCKS_PORT socks port listening on $LISTEN_PORT"
	SERVICE_FILE="/etc/systemd/system/privoxy$INSTANCE.service"
	mkdir -p $CONFDIR
	mkdir -p $LOGDIR
	echo "forward-socks5t   /               127.0.0.1:$SOCKS_PORT ." > $CONF
	echo "logdir $LOGDIR" >> $CONF
	echo "listen-address  localhost:$LISTEN_PORT" >> $CONF
	cat $ETCDIR/privoxy.config.default >> $CONF

cat << EOF > $SERVICE_FILE
[Unit]
Description=Privacy enhancing HTTP Proxy

[Service]
Environment=PIDFILE=/var/run/privoxy$INSTANCE.pid
Environment=OWNER=privoxy
Environment=CONFIGFILE=$CONF
Type=forking
PIDFile=/var/run/privoxy$INSTANCE.pid
ExecStart=/usr/sbin/privoxy --pidfile \$PIDFILE --user \$OWNER \$CONFIGFILE
ExecStopPost=/bin/rm -f \$PIDFILE
SuccessExitStatus=15

[Install]
WantedBy=multi-user.target
EOF

	systemctl daemon-reload
	systemctl stop privoxy$INSTANCE.service
	systemctl start privoxy$INSTANCE.service
done
 
