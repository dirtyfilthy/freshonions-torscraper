#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
BASEDIR=$DIR/..
$BASEDIR/scripts/kill.sh delegate
$BASEDIR/scripts/kill.sh haproxy
$BASEDIR/scripts/kill.sh tor
