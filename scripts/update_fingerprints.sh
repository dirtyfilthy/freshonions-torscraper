#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
DOMAINS=`mktemp`
TOUCHFILE="$VARDIR/last_fingerprint_check"
$SCRIPTDIR/domains_since_and_touch.py $TOUCHFILE > $DOMAINS
cat $DOMAINS | xargs -n 1 -P 10 $SCRIPTDIR/check_fingerprint.sh
