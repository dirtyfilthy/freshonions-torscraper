#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
cat $1 | xargs -n 1 $SCRIPTDIR/push.sh
