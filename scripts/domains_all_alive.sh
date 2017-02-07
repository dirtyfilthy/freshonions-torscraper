#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
$SCRIPTDIR/domains_all_alive.py
