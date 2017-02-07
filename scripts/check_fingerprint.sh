#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
HOST=$1
TIMEOUT=60
FPRINT=`ssh-keyscan -T $TIMEOUT $HOST 2>/dev/null | grep ssh-rsa | cut -f 3 -d ' '`
if [ -n "$FPRINT" ]; then
	echo "Got $FPRINT for $HOST"
	$SCRIPT/add_ssh_fingerprint.py $HOST $FPRINT
done
