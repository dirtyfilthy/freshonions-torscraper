#!/bin/sh
export BASEDIR=$DIR/..
export SCRIPTDIR=$BASEDIR/scripts
export ETCDIR=$BASEDIR/etc
export PYTHONPATH=$PYTHONPATH:$BASEDIR/lib
. $BASEDIR/etc/proxy
