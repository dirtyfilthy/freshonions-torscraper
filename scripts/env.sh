#!/bin/sh
export BASEDIR=$DIR/..
export SCRIPTDIR=$BASEDIR/scripts
export ETCDIR=$BASEDIR/etc
export VARDIR=$BASEDIR/var
export PYTHONPATH=$PYTHONPATH:$BASEDIR/lib
. $BASEDIR/etc/proxy
