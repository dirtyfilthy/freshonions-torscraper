#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
BASEDIR=$DIR/..
export PYTHONPATH=$PYTHONPATH:$BASEDIR/lib
. $BASEDIR/etc/proxy
cd $BASEDIR
scrapy crawl tor -a test=no
