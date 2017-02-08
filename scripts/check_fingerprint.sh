#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
HOST=$1
TIMEOUT=60
FPRINT=`torify $SCRIPTDIR/ssh_fingerprint.py $HOST 2>/dev/null | grep ssh-rsa | cut -f 2 -d ' '`
if [ -n "$FPRINT" ]; then
	echo "Got $FPRINT for $HOST"
	$SCRIPTDIR/add_ssh_fingerprint.py "$HOST" "$FPRINT"
else
	echo "No fingerprint for $HOST"
fi