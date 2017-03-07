#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
LOGFILE=`mktemp`
TEMP1=`mktemp`
scp torlogs@growl:/var/log/tor/info.log $LOGFILE | grep -E -o '[0-7a-zA_Z]+
cat $LOGFILE | 
