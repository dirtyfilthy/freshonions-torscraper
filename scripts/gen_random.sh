#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
python $SCRIPTDIR/gen_random.py $1
