#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
python $SCRIPTDIR/detect_clones.py
$SCRIPTDIR/clean_clone_groups.sh
