#!/bin/sh
export PATH=$PATH:/bin/:/sbin/:/usr/bin/:/usr/sbin:/usr/local/bin
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/../scripts/env.sh
while true
do
  $SCRIPTDIR/test_up.sh
done
